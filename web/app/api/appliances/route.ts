import { proxy } from "@/lib/proxy";

export async function GET() {
  return proxy("/v1/appliances");
}
