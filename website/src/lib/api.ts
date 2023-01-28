import axios from "axios";

import { OasstError } from "./oasst_api_client";

const headers = {
  "Content-Type": "application/json",
};

const api = axios.create({
  headers,
});

export const get = (url: string) => api.get(url).then((res) => res.data);

export const post = (url: string, { arg: data }) => api.post(url, data).then((res) => res.data);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const err = error?.response?.data;
    throw new OasstError(err?.message ?? error, err?.errorCode, error?.response?.httpStatusCode || -1);
  }
);

export default api;
