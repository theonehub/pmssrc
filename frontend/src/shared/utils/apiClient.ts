// ============================================================================
//  Compatibility Wrapper around the new BaseAPI
//  -------------------------------------------------
//  The project previously relied on an axios-based apiClient that returned a
//  full AxiosResponse object (so most legacy code expects `response.data`).
//  To avoid a huge breaking change during the integration phase, we implement
//  a thin shim that internally delegates all calls to the new BaseAPI while
//  preserving the old response shape.
// ============================================================================

import { AxiosRequestConfig, AxiosResponse } from 'axios';
import { BaseAPI } from '../api/baseApi';

type DataWrapper<T> = { data: T } & Omit<AxiosResponse<T>, 'data'>;

const base = BaseAPI.getInstance();

// Helper to wrap plain data into an Axios-like response object
const wrap = <T>(data: T): DataWrapper<T> => {
  return {
    data,
    status: 200,
    statusText: 'OK',
    headers: {},
    config: {
      headers: {} as any,
    } as any,
    request: undefined as any,
  };
};

const apiClient = {
  get: async <T = any>(url: string, config?: AxiosRequestConfig): Promise<DataWrapper<T>> => {
    const data = await base.get<T>(url, config);
    return wrap<T>(data);
  },
  post: async <T = any>(url: string, body?: any, config?: AxiosRequestConfig): Promise<DataWrapper<T>> => {
    const data = await base.post<T>(url, body, config);
    return wrap<T>(data);
  },
  put: async <T = any>(url: string, body?: any, config?: AxiosRequestConfig): Promise<DataWrapper<T>> => {
    const data = await base.put<T>(url, body, config);
    return wrap<T>(data);
  },
  patch: async <T = any>(url: string, body?: any, config?: AxiosRequestConfig): Promise<DataWrapper<T>> => {
    const data = await base.patch<T>(url, body, config);
    return wrap<T>(data);
  },
  delete: async <T = any>(url: string, config?: AxiosRequestConfig): Promise<DataWrapper<T>> => {
    const data = await base.delete<T>(url, config);
    return wrap<T>(data);
  },
  // File upload / download helpers keep their original signatures
  upload: base.upload.bind(base),
  download: base.download.bind(base),
};

// Named helpers replicating legacy signatures (returning *plain* data)
export const get = async <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> =>
  base.get<T>(url, config);

export const post = async <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> =>
  base.post<T>(url, data, config);

export const put = async <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> =>
  base.put<T>(url, data, config);

export const del = async <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> =>
  base.delete<T>(url, config);

export const patch = async <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> =>
  base.patch<T>(url, data, config);

export default apiClient;
