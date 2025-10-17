import {
  RequestOtpPayload,
  RequestOtpResponse,
  RequestVerifyPayload,
  RequestVerifyResponse,
} from "@/types";
import baseApi, { baseURL } from "../base";
import axios from "axios";

export async function requestOtp(data: RequestOtpPayload) {
  const res = await axios.post<RequestOtpResponse>(
    baseURL + "accounts/request-otp/",
    data,
  );
  return res.data;
}

export async function verifyOtp(data: RequestVerifyPayload) {
  const res = await axios.post<RequestVerifyResponse>(
    baseURL + "accounts/verify-otp/",
    data,
  );
  return res.data;
}

export async function refreshToken(data: { refresh: string }) {
  const res = await baseApi.post<{ access: string; refresh: string }>(
    "/accounts/token/refresh/",
    data,
  );
  return res.data;
}
