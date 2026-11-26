import apiClient from './client';
import type { ChatResponse, ConversationDetail, ConversationList } from '@/types';

export const conversationApi = {
  chat: async (patientId: number, question: string, conversationId: number | null): Promise<ChatResponse> =>
    (await apiClient.post<ChatResponse>(`/patients/${patientId}/chat`, { question, conversation_id: conversationId })).data,
  list: async (patientId: number, skip = 0, limit = 50): Promise<ConversationList> =>
    (await apiClient.get<ConversationList>(`/patients/${patientId}/conversations`, { params: { skip, limit } })).data,
  detail: async (patientId: number, conversationId: number): Promise<ConversationDetail> =>
    (await apiClient.get<ConversationDetail>(`/patients/${patientId}/conversations/${conversationId}`)).data,
};
