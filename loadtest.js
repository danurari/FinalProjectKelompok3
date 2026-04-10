import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  insecureSkipTLSVerify: true,

  stages: [
    { duration: "30s", target: 50 },
    { duration: "2m", target: 200 },
    { duration: "30s", target: 0 },
  ],

  thresholds: {
    http_req_failed: ["rate==0"],
    http_req_duration: ["p(95)<2000"],
  },
};

export default function () {
  const url = "https://layananbuku.netdev/";

  const res = http.get(url);

  check(res, {
    "status is 200 OK": (r) => r.status === 200,
  });

  sleep(1);
}
