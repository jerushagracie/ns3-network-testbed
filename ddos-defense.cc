#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"

using namespace ns3;

Ptr<PacketSink> g_sink;
uint64_t g_last = 0;

void PrintThroughput()
{
    uint64_t now = g_sink->GetTotalRx();
    std::cout << "THROUGHPUT " << Simulator::Now().GetSeconds() << " " << (now - g_last) * 8.0 / 1e6 << std::endl;
    g_last = now;
    Simulator::Schedule(Seconds(1.0), &PrintThroughput);
}

int main(int argc, char *argv[])
{
    double rate = 4;
    double attackStart = 8;
    double blockAt = 20;
    double fwLimit = 0;
    double bw = 5;
    uint32_t nAtt = 5;
    std::string prefix = "ddos-def";
    CommandLine cmd;
    cmd.AddValue("rate", "Mbps per attacker", rate);
    cmd.AddValue("attackStart", "attack start time", attackStart);
    cmd.AddValue("blockAt", "time attackers are blocked", blockAt);
    cmd.AddValue("fwLimit", "static firewall cap on total attack Mbps (0 = off)", fwLimit);
    cmd.AddValue("bw", "bottleneck Mbps", bw);
    cmd.AddValue("nAtt", "number of attackers", nAtt);
    cmd.AddValue("prefix", "pcap prefix", prefix);
    cmd.Parse(argc, argv);

    NodeContainer legit, r1, r2, server, attackers;
    legit.Create(1);
    r1.Create(1);
    r2.Create(1);
    server.Create(1);
    attackers.Create(nAtt);

    PointToPointHelper fast;
    fast.SetDeviceAttribute("DataRate", StringValue("100Mbps"));
    fast.SetChannelAttribute("Delay", StringValue("2ms"));

    PointToPointHelper slow;
    slow.SetDeviceAttribute("DataRate", StringValue(std::to_string(bw) + "Mbps"));
    slow.SetChannelAttribute("Delay", StringValue("10ms"));

    NetDeviceContainer d1 = fast.Install(legit.Get(0), r1.Get(0));
    NetDeviceContainer d3 = slow.Install(r1.Get(0), r2.Get(0));
    NetDeviceContainer d4 = fast.Install(r2.Get(0), server.Get(0));
    std::vector<NetDeviceContainer> da;
    for (uint32_t i = 0; i < nAtt; ++i)
    {
        da.push_back(fast.Install(attackers.Get(i), r1.Get(0)));
    }

    InternetStackHelper stack;
    stack.InstallAll();

    Ipv4AddressHelper address;
    address.SetBase("10.1.1.0", "255.255.255.0");
    address.Assign(d1);
    address.SetBase("10.1.3.0", "255.255.255.0");
    address.Assign(d3);
    address.SetBase("10.1.4.0", "255.255.255.0");
    Ipv4InterfaceContainer i4 = address.Assign(d4);
    for (uint32_t i = 0; i < nAtt; ++i)
    {
        std::string base = "10.2." + std::to_string(i + 1) + ".0";
        address.SetBase(base.c_str(), "255.255.255.0");
        address.Assign(da[i]);
    }

    Ipv4Address serverIp = i4.GetAddress(1);

    PacketSinkHelper tcpSink("ns3::TcpSocketFactory", InetSocketAddress(Ipv4Address::GetAny(), 8080));
    ApplicationContainer sinkApp1 = tcpSink.Install(server.Get(0));
    sinkApp1.Start(Seconds(0));
    sinkApp1.Stop(Seconds(20));

    PacketSinkHelper udpSink("ns3::UdpSocketFactory", InetSocketAddress(Ipv4Address::GetAny(), 9));
    ApplicationContainer sinkApp2 = udpSink.Install(server.Get(0));
    sinkApp2.Start(Seconds(0));
    sinkApp2.Stop(Seconds(20));

    BulkSendHelper bulk("ns3::TcpSocketFactory", InetSocketAddress(serverIp, 8080));
    bulk.SetAttribute("MaxBytes", UintegerValue(0));
    ApplicationContainer legitApp = bulk.Install(legit.Get(0));
    legitApp.Start(Seconds(1));
    legitApp.Stop(Seconds(20));

    OnOffHelper onoff("ns3::UdpSocketFactory", InetSocketAddress(serverIp, 9));
    double effRate = (fwLimit > 0 && fwLimit / nAtt < rate) ? fwLimit / nAtt : rate;
    onoff.SetAttribute("DataRate", StringValue(std::to_string(effRate) + "Mbps"));
    onoff.SetAttribute("PacketSize", UintegerValue(1000));
    onoff.SetAttribute("OnTime", StringValue("ns3::ConstantRandomVariable[Constant=1.0]"));
    onoff.SetAttribute("OffTime", StringValue("ns3::ConstantRandomVariable[Constant=0.0]"));
    ApplicationContainer attackApp = onoff.Install(attackers);
    attackApp.Start(Seconds(attackStart));
    attackApp.Stop(Seconds(blockAt));

    Ipv4GlobalRoutingHelper::PopulateRoutingTables();

    slow.EnablePcap(prefix, d3.Get(0), true);
    g_sink = DynamicCast<PacketSink>(sinkApp1.Get(0));
    Simulator::Schedule(Seconds(1.0), &PrintThroughput);

    Simulator::Stop(Seconds(20));
    Simulator::Run();
    Simulator::Destroy();
    return 0;
}
