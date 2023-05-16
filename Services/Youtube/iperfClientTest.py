import iperf3


client = iperf3.Client()
client.duration = 2
client.server_hostname = "127.0.0.1"
client.port = 3000


print('Connecting to {0}:{1}'.format(client.server_hostname, client.port))
result = client.run()

if result.error:
    print(result.error)
else:
    print('')
    print('Test completed:')
    print('  started at         {0}'.format(result.time))
    print('  bytes transmitted  {0}'.format(result.sent_bytes))
    print('  retransmits        {0}'.format(result.retransmits))
    print('  avg cpu load       {0}%\n'.format(result.local_cpu_total))

    print('Average transmitted data in all sorts of networky formats:')
    print('  bits per second      (bps)   {0}'.format(result.sent_bps))
    print('  Kilobits per second  (kbps)  {0}'.format(result.sent_kbps))
    print('  Megabits per second  (Mbps)  {0}'.format(result.sent_Mbps))
    print('  KiloBytes per second (kB/s)  {0}'.format(result.sent_kB_s))
    print('  MegaBytes per second (MB/s)  {0}'.format(result.sent_MB_s))


    print('Average received data in all sorts of networky formats:')
    print('  bits per second      (bps)   {0}'.format(result.received_bps))
    print('  Kilobits per second  (kbps)  {0}'.format(result.received_kbps))
    print('  Megabits per second  (Mbps)  {0}'.format(result.received_Mbps))
    print('  KiloBytes per second (kB/s)  {0}'.format(result.received_kB_s))
    print('  MegaBytes per second (MB/s)  {0}'.format(result.received_MB_s))

del client
client2 = iperf3.Client()
client2.duration = 5
client2.server_hostname = "127.0.0.1"
client2.port = 3000
client2.protocol="udp"

print('Connecting to {0}:{1}'.format(client2.server_hostname, client2.port))
result2 = client2.run()

if result2.error:
    print(result2.error)
else:
    print('')
    print('Test completed:')
    print('  started at         {0}'.format(result2.time))
    print('  avg cpu load       {0}%\n'.format(result2.local_cpu_total))

    print('Average transmitted data in all sorts of networky formats:')
    print('  bytes     (bytes)   {0}'.format(result2.bytes))
    print('  Kilobits per second  (kbps)  {0}'.format(result2.kbps))
    print('  Megabits per second  (Mbps)  {0}'.format(result2.Mbps))
    print('  KiloBytes per second (kB/s)  {0}'.format(result2.kB_s))
    print('  MegaBytes per second (MB/s)  {0}'.format(result2.MB_s))
    print('  Lost packages                {0}'.format(result2.lost_packets))
    print('  Lost percent                 {0}'.format(result2.lost_percent))
    print('  Jitter               (ms)    {0}'.format(result2.jitter_ms))
    