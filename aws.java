package com.utstar.aaa.controller.webservice;

import com.utstar.aaa.common.constant.AaaSpringConfig;
import com.utstar.aaa.common.utils.NewOldAaaSwitchUtils;
import com.utstar.aaa.common.utils.StringUtils;
import com.utstar.aaa.common.utils.UserTokenUtils;
import com.utstar.aaa.service.SubscribeService;
import com.utstar.aaa.service.SubscribeServiceByPayid;
import com.utstar.aaa.webservice.generator.subscribe.SubscribeRequestVO;
import com.utstar.aaa.webservice.generator.subscribe.SubscribeResponseVO;
import com.utstar.aaa.webservice.generator.subscribe.SubscribeServiceSoapImpl;
import javax.annotation.Resource;
import javax.jws.WebService;
import org.apache.cxf.endpoint.Client;
import org.apache.cxf.frontend.ClientProxy;
import org.apache.cxf.jaxws.JaxWsProxyFactoryBean;
import org.apache.cxf.transport.http.HTTPConduit;
import org.apache.cxf.transports.http.configuration.ConnectionType;
import org.apache.cxf.transports.http.configuration.HTTPClientPolicy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

@WebService(serviceName = "SubscribeServiceSoapImplService", portName = "SubscribeServiceSoapImpl", targetNamespace = "http://subscribe.webservice.iptv3a.shtel.com", endpointInterface = "com.utstar.aaa.webservice.generator.subscribe.SubscribeServiceSoapImpl")
@Component("subscribeServiceSoapImplImpl")
public class SubscribeServiceSoapImplImpl implements SubscribeServiceSoapImpl {
  private static final Logger LOG = LoggerFactory.getLogger(SubscribeServiceSoapImplImpl.class.getName());
  
  @Autowired
  SubscribeService subscribeService;
  
  @Autowired
  SubscribeServiceByPayid subscribeServiceByPayid;
  
  @Resource(name = "aaaSpringConfig")
  private AaaSpringConfig aaaSpringConfig;
  
  public SubscribeResponseVO instantSubscribe(SubscribeRequestVO request) {
    SubscribeResponseVO response = null;
    String userid = request.getUserID();
    if (userid == null || "".equals(userid)) {
      String userToken = request.getUserToken();
      userid = UserTokenUtils.getUseridFromUserToken(userToken);
      LOG.info("SubscribeServiceSoapImplImpl instantSubscribe userid is null so from userToken is {} get userid is {}", userToken, userid);
    } 
    if (NewOldAaaSwitchUtils.dispatcherToNewAaaFlag(userid)) {
      LOG.info("SubscribeServiceSoapImplImpl instantSubscribe dispatcher [new aaa] req is {}", request
          .toString());
      int limitBindingPayidUserid = this.aaaSpringConfig.getLimitBindingPayidUserid();
      response = this.subscribeService.instantSubscribe(request);
      if (limitBindingPayidUserid > 0 && 
        StringUtils.notNullEmpty(request.getPayID()))
        response = this.subscribeServiceByPayid.instantSubscribe(request); 
      LOG.info("SubscribeServiceSoapImplImpl instantSubscribe dispatcher [new aaa] rsp is {}", response
          .toString());
    } else {
      LOG.info("SubscribeServiceSoapImplImpl instantSubscribe dispatcher [old aaa] req is {}", request
          .toString());
      SubscribeServiceSoapImpl soapclient = createSoapClient();
      response = soapclient.instantSubscribe(request);
      if (response != null) {
        LOG.info("SubscribeServiceSoapImplImpl instantSubscribe dispatcher [old aaa] rsp is {}", response
            .toString());
      } else {
        LOG.info("SubscribeServiceSoapImplImpl instantSubscribe dispatcher [old aaa] rsp is null");
      } 
    } 
    return response;
  }
  
  private SubscribeServiceSoapImpl createSoapClient() {
    JaxWsProxyFactoryBean jaxWsProxyFactoryBean = new JaxWsProxyFactoryBean();
    jaxWsProxyFactoryBean.setAddress(this.aaaSpringConfig.getOldAaaUrl2());
    jaxWsProxyFactoryBean.setServiceClass(SubscribeServiceSoapImpl.class);
    SubscribeServiceSoapImpl soapclient = (SubscribeServiceSoapImpl)jaxWsProxyFactoryBean.create();
    Client client = ClientProxy.getClient(soapclient);
    HTTPConduit conduit = (HTTPConduit)client.getConduit();
    HTTPClientPolicy policy = conduit.getClient();
    policy.setConnection(ConnectionType.CLOSE);
    return soapclient;
  }
}
