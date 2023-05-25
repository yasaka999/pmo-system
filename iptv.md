    ```mermaid
    C4Context
      title C4 Model for Automatic Testing System of IPTV System

      Enterprise_Boundary(b0, "IPTV Provider Boundary") {
        Person(User, "User", "A user of the IPTV system")
        System(IPTVSystem, "IPTV System", "A television broadcasting system delivered over a network using Internet Protocol (IP) instead of traditional terrestrial, satellite signal or cable television formats.")
        System(AutoTestingSystem, "Automatic Testing System", "A system used to automate the testing process of IPTV services.")

        Enterprise_Boundary(b1, "Testing Unit Boundary") {

          System(VideoServer, "Video Server", "A server that stores and delivers video content.")
          System(StreamingServer, "Streaming Server", "A server that delivers streaming media content.")
          System(ContentDeliveryNetwork, "Content Delivery Network", "A globally distributed network of servers that serves content proximate to end-users.")
        }

        System_Ext(CentralDatabase, "Central Database", "Stores all the logs, errors and usage data related to the IPTV system and the automatic testing system.")
      }

      BiRel(User, AutoTestingSystem, "Uses")
      BiRel(AutoTestingSystem, IPTVSystem, "Tests")
      BiRel(AutoTestingSystem, VideoServer, "Tests")
      BiRel(AutoTestingSystem, StreamingServer, "Tests")
      BiRel(AutoTestingSystem, ContentDeliveryNetwork, "Tests")
      Rel(AutoTestingSystem, CentralDatabase, "Writes logs and test results to")

      UpdateElementStyle(User, $fontColor="red", $bgColor="grey", $borderColor="red")
      UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```