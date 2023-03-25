import axios from "axios";

import { OasstError } from "./oasst_api_client";

const headers = {
  "Content-Type": "application/json",
};

const api = axios.create({ headers });

export const get = (url: string) => api.get(url).then((res) => res.data);

export const post = (url: string, { arg: data }) => api.post(url, data).then((res) => res.data);

export const del = (url: string) => api.delete(url).then((res) => res.data);

export const put = (url: string, { arg: data }) => api.put(url, data).then((res) => res.data);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const err = error?.response?.data;
    throw new OasstError({
      message: err?.message || "",
      errorCode: err?.errorCode,
      httpStatusCode: error?.response?.httpStatusCode || -1,
      method: err?.config?.method,
      path: err?.config?.url,
    });
  }
);

export default api;
