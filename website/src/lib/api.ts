/* eslint-disable @typescript-eslint/no-explicit-any */
import axios from "axios";

import { OasstError } from "./oasst_api_client";

const headers = {
  "Content-Type": "application/json",
};

const api = axios.create({ headers });

export const get = (url: string) => api.get(url).then((res) => res.data);

export const post = (url: string, data?: { arg: any }) => api.post(url, data?.arg).then((res) => res.data);

export const del = (url: string) => api.delete(url).then((res) => res.data);

export const put = (url: string, data?: { arg: any }) => api.put(url, data?.arg).then((res) => res.data);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const err = error?.response?.data;
    throw new OasstError({
      message: err?.message ?? error.response.data ?? "",
      errorCode: err?.errorCode,
      httpStatusCode: error?.response?.httpStatusCode ?? error.response?.status ?? -1,
      method: err?.config?.method ?? error.config?.method,
      path: err?.config?.url ?? error.config?.url,
    });
  }
);

export default api;
