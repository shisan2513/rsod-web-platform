import request from '../utils/request'

export const detectSingleImage = (data) => {
  return request({
    url: '/detection/single',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const detectBatchImages = (data) => {
  return request({
    url: '/detection/batch',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const getDetectionHistory = (params) => {
  return request({
    url: '/detection/history',
    method: 'get',
    params
  })
}

export const getDetectionDetail = (id) => {
  return request({
    url: `/detection/detail/${id}`,
    method: 'get'
  })
}

export const getTargetList = () => {
  return request({
    url: '/targets/list',
    method: 'get'
  })
}

export const detectFrame = (data) => {
  return request({
    url: '/detection/camera/detect',
    method: 'post',
    data
  })
}

export const startCameraDetection = (data) => {
  return request({
    url: '/detection/camera/start',
    method: 'post',
    data
  })
}

export const stopCameraDetection = () => {
  return request({
    url: '/detection/camera/stop',
    method: 'post'
  })
}

export const getCameraStatus = () => {
  return request({
    url: '/detection/camera/status',
    method: 'get'
  })
}

export const detectRealtimeFrame = (data) => {
  return request({
    url: '/video-detection/realtime-frame',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 10000
  })
}
