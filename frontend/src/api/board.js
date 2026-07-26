// 게시판 API 모듈
import api from './index';

export const boardApi = {
  // 게시글 목록 조회
  getBoards(boardType = 'free') {
    return api.get(`/api/board/${boardType}`);
  },

  // 게시글 단건 조회
  getBoard(boardType, boardId) {
    return api.get(`/api/board/${boardType}/${boardId}`);
  },

  // 게시글 작성 (회원/비회원 공용)
  createBoard(boardType, data) {
    return api.post(`/api/board/${boardType}`, data);
  },

  // 게시글 수정
  updateBoard(boardType, boardId, data) {
    return api.put(`/api/board/${boardType}/${boardId}`, data);
  },

  // 게시글 삭제
  deleteBoard(boardType, boardId, password = null) {
    return api.post(`/api/board/${boardType}/${boardId}/delete`, { password });
  }
};
