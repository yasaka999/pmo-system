select ee.days,
       nvl(dg_5, 0),
       nvl(td_jc1, 0),
       nvl(dg_6, 0),
       nvl(td_jc3, 0),
       nvl(dg_3, 0),
       nvl(td_lx2, 0),
       nvl(dg_1, 0),
       nvl(td_jc2, 0),
       nvl(dg_4, 0),
       nvl(td_jc4, 0),
       nvl(dg_9, 0),
       nvl(td_lx5, 0),
       nvl(dg_10, 0),
       nvl(td_lx6, 0),
       nvl(dg_11, 0),
       nvl(td_lx7, 0),
       nvl(dg_12, 0),
       nvl(td_lx8, 0),
       nvl(dg_7, 0),
       nvl(td_jc5, 0),
       nvl((nvl(dg_2, 0) + nvl(dg_8, 0)), 0) as "other_order",
       nvl((nvl(td_jc8, 0) + nvl(td_jc6, 0) + nvl(td_jc7, 0)), 0) as "other_disorser",
       nvl((nvl(dg_5, 0) + nvl(dg_6, 0) + nvl(dg_3, 0) + nvl(dg_1, 0) +
           nvl(dg_4, 0) + nvl(dg_2, 0) + nvl(dg_7, 0) + nvl(dg_8, 0) +
           nvl(dg_10, 0) + nvl(dg_11, 0) + nvl(dg_12, 0) + nvl(dg_4, 9)),
           0) as "order_sum",
       nvl((td_jc1 + td_jc3 + nvl(td_lx2, 0) + td_jc2 + td_jc4 + td_jc5 +
           td_jc8 + td_jc6 + td_jc7 + nvl(td_lx5, 0) + nvl(td_lx6, 0) +
           nvl(td_lx7, 0) + nvl(td_lx8, 0)),
           0) as "disorder_sum"
  from (select *
          from (select a.date1,
                       max(case package1
                             when 21 then
                              sum1
                             else
                              0
                           end) td_lx1,
                       max(case package1
                             when 23 then
                              sum1
                             else
                              0
                           end) td_lx2,
                       max(case package1
                             when 16 then
                              sum1
                             else
                              0
                           end) td_lx3,
                       max(case package1
                             when 5 then
                              sum1
                             else
                              0
                           end) td_lx4,
                       max(case package1
                             when 32 then
                              sum1
                             else
                              0
                           end) td_lx5,
                       max(case package1
                             when 33 then
                              sum1
                             else
                              0
                           end) td_lx6,
                       max(case package1
                             when 34 then
                              sum1
                             else
                              0
                           end) td_lx7,
                       max(case package1
                             when 35 then
                              sum1
                             else
                              0
                           end) td_lx8
                  from (select to_char(i.completedate, 'yyyy/mm/dd') date1,
                               i.iptvproductid package1,
                               count(1) sum1
                          from iptvproductorder i
                         where i.optype = 3
                              --  and i.completedate > to_date('2020/9/1', 'yyyy/mm/dd')
                           and to_char(i.completedate, 'yyyy/mm/dd') <
                               to_char(sysdate, 'yyyy/mm/dd')
                           and i.iptvproductid in
                               (select p.iptvproductid
                                  from iptvproduct p
                                 where p.status = 1
                                   and nvl(p.chargingtype, 99) != 2)
                         group by to_char(i.completedate, 'yyyy/mm/dd'),
                                  i.iptvproductid
                        
                        ) a
                 group by a.date1) aa
          full join (select to_char((trunc(sysdate - 1000) + rownum),
                                   'yyyy/mm/dd') as days
                      from dual
                    connect by rownum <= 1000) dd
            on aa.date1 = dd.days) ee
  full join (select *
               from (select b.date2,
                            max(case package1
                                  when 31 then
                                   sum1
                                  else
                                   0
                                end) td_jc1,
                            max(case package1
                                  when 20 then
                                   sum1
                                  else
                                   0
                                end) td_jc2,
                            max(case package1
                                  when 22 then
                                   sum1
                                  else
                                   0
                                end) td_jc3,
                            max(case package1
                                  when 24 then
                                   sum1
                                  else
                                   0
                                end) td_jc4,
                            max(case package1
                                  when 25 then
                                   sum1
                                  else
                                   0
                                end) td_jc5,
                            max(case package1
                                  when 30 then
                                   sum1
                                  else
                                   0
                                end) td_jc6,
                            max(case package1
                                  when 26 then
                                   sum1
                                  else
                                   0
                                end) td_jc7,
                            max(case package1
                                  when 18 then
                                   sum1
                                  else
                                   0
                                end) td_jc8
                       from (
                             
                             select to_char(i.completedate, 'yyyy/mm/dd') date2,
                                     i.iptvproductid package1,
                                     count(1) sum1
                               from iptvproductorder i
                              where i.optype = 2
                                   --  and i.completedate > to_date('2020/9/1', 'yyyy/mm/dd')
                                and to_char(i.completedate, 'yyyy/mm/dd') <
                                    to_char(sysdate, 'yyyy/mm/dd')
                                and i.iptvproductid in
                                    (select p.iptvproductid
                                       from iptvproduct p
                                      where p.status = 1
                                        and p.chargingtype = 2)
                              group by to_char(i.completedate, 'yyyy/mm/dd'),
                                        i.iptvproductid
                             
                             ) b
                      group by b.date2) bb
               full join (select to_char((trunc(sysdate - 1000) + rownum),
                                        'yyyy/mm/dd') as days
                           from dual
                         connect by rownum <= 1000) dd
                 on bb.date2 = dd.days) ff

    on ee.days = ff.days
  full join (select *
               from (select date3,
                            max(case package1
                                  when 20 then
                                   sum1
                                  else
                                   0
                                end) as dg_1,
                            max(case package1
                                  when 30 then
                                   sum1
                                  else
                                   0
                                end) dg_2,
                            max(case package1
                                  when 23 then
                                   sum1
                                  else
                                   0
                                end) dg_3,
                            max(case package1
                                  when 24 then
                                   sum1
                                  else
                                   0
                                end) dg_4,
                            max(case package1
                                  when 31 then
                                   sum1
                                  else
                                   0
                                end) dg_5,
                            max(case package1
                                  when 22 then
                                   sum1
                                  else
                                   0
                                end) dg_6,
                            max(case package1
                                  when 25 then
                                   sum1
                                  else
                                   0
                                end) dg_7,
                            max(case package1
                                  when 26 then
                                   sum1
                                  else
                                   0
                                end) dg_8,
                            max(case package1
                                  when 32 then
                                   sum1
                                  else
                                   0
                                end) dg_9,
                            max(case package1
                                  when 33 then
                                   sum1
                                  else
                                   0
                                end) dg_10,
                            max(case package1
                                  when 34 then
                                   sum1
                                  else
                                   0
                                end) dg_11,
                            max(case package1
                                  when 35 then
                                   sum1
                                  else
                                   0
                                end) dg_12
                       from (select to_char(i.operatetime, 'yyyy/mm/dd') date3,
                                    i.iptvproductid package1,
                                    count(1) sum1
                               from iptvproductorder i
                              where i.optype = 2
                             --and i.operatetime > to_date('2020/9/1','yyyy/mm/dd')
                              group by to_char(i.operatetime, 'yyyy/mm/dd'),
                                       i.iptvproductid) a
                      group by date3) cc
               full join (select to_char((trunc(sysdate - 1000) + rownum),
                                        'yyyy/mm/dd') as days
                           from dual
                         connect by rownum <= 1000) dd
                 on cc.date3 = dd.days) gg
    on gg.days = ff.days
 order by ee.days desc


