import { removeTokens, storeTokens, tokens } from "@/hooks/useAuth";
import axios from "axios";
import qs from "qs";
import { refreshToken } from "./auth/auth.api";
export const baseURL = "http://127.0.0.1:8000/api/";
// export const baseURL = "http://localhost:3000/api/";ch
const baseApi = axios.create({
  baseURL, // public server url or ip
  paramsSerializer: (params) => qs.stringify(params, { arrayFormat: "repeat" }),
});

export default baseApi;

baseApi.interceptors.request.use(
  function (config) {
    if (tokens.access) {
      config.headers.Authorization = "Bearer " + tokens.access;
    }
    return config;
  },
  function (error) {
    // Do something with request error
    return Promise.reject(error);
  },
);

// Add a response interceptor
baseApi.interceptors.response.use(
  function (response) {
    // Any status code that lie within the range of 2xx cause this function to trigger
    // Do something with response data
    return response;
  },
  function (error) {
    if (error.response && error.response.status === 401) {
      // Handle unauthorized error
      console.error("Unauthorized access attempt");
      // Try to get new access token
      refreshToken({ refresh: tokens.refresh })
        .then((res) => {
          // Update access token
          storeTokens(res.access, res.refresh);
          error.config.headers.Authorization = "Bearer " + res.access;
          // Retry original request
          return baseApi(error.config);
        })
        .catch((error) => {
          // Remove token from local storage if failed to get new access token
          removeTokens();
          // Redirect to login or perform other actions
          console.log(error);
          window.location.href = "/";
        });
    }
    return Promise.reject(error);
  },
);
