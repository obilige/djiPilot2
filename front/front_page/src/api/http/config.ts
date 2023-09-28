export const CURRENT_CONFIG = {

  // license
  appId: '131583',  // You need to go to the development website to apply.
  appKey: '6b91e021824438126c5c8534f449e16',  // You need to go to the development website to apply.
  appLicense: 'bRVQNN3IkxSXuy5D62KMyV1PKXlTQWadDnGFnPnOiaKkEFoWm9dgDGLR9VT1snckVYH2p9Y/DuN4+bou8vLMThPgrOCVJWFFrcqUPxLL3h3xZtXxvIl0nMFh/fGToZAGpvu98D9Oip5ProT5QXn2u4V8INgGiCT6xFt8ZktGUNI=', // You need to go to the development website to apply.
  
  // http
  baseURL: 'http://211.189.131.66:8095/back/', // This url must end with "/". Example: 'http://192.168.1.1:6789/'
  websocketURL: 'ws://211.189.131.66:8095/back/api/v1/ws',  // Example: 'ws://192.168.1.1:6789/api/v1/ws'

  // livestreaming
  // RTMP  Note: This IP is the address of the streaming server. If you want to see livestream on web page, you need to convert the RTMP stream to WebRTC stream.
  rtmpURL: 'rtmp://211.189.131.66/app/stream/',  // Example: 'rtmp://192.168.1.1/live/' 
  // GB28181 Note:If you don't know what these parameters mean, you can go to Pilot2 and select the GB28181 page in the cloud platform. Where the parameters same as these parameters.
  gbServerIp: 'Please enter the server ip.',
  gbServerPort: 'Please enter the server port.',
  gbServerId: 'Please enter the server id.',
  gbAgentId: 'Please enter the agent id',
  gbPassword: 'Please enter the agent password',
  gbAgentPort: 'Please enter the local port.',
  gbAgentChannel: 'Please enter the channel.',
  // RTSP
  rtspUserName: 'aaa',
  rtspPassword: 'bbb',
  rtspPort: '8554',
  // Agora
  agoraAPPID: 'Please enter the agora app id.',
  agoraToken: 'Please enter the agora temporary token.',
  agoraChannel: 'Please enter the agora channel.',

  // map 
  // You can apply on the AMap website.
  amapKey: 'Please enter the amap key.',

}
