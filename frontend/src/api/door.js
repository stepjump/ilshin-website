// src/api/door.js
import axios from 'axios';

// 백엔드 API 기본 URL (Render 서버)
const API_URL = 'https://ilshin-website.onrender.com/api/door-info/';

export const doorApi = {
  // 전체 도어 정보 목록 가져오기
  getDoorInfos: () => axios.get(API_URL),

  // 단일 도어 정보 가져오기 (필요시)
  getDoorInfoById: (id) => axios.get(`${API_URL}/${id}`)
};