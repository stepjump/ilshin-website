// frontend/src/api/door.js
import axios from 'axios';

// 백엔드 Base URL (Render)
const API_BASE_URL = 'https://ilshin-website.onrender.com/api/door-info';

export const doorApi = {
  // 전체 도어 목록 조회
  getDoorInfos: () => axios.get(`${API_BASE_URL}/`),

  // ★ 활성화된 메인 도어 정보 조회 (/api/door-info/active)
  getActiveDoorInfo: () => axios.get(`${API_BASE_URL}/active`),

  // 단일 도어 정보 조회
  getDoorInfoById: (id) => axios.get(`${API_BASE_URL}/${id}`)
};