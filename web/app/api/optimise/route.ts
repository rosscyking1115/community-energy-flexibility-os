import { proxy } from "@/lib/proxy";

export async function POST(req: Request) {
  return proxy("/v1/optimise", { method: "POST", body: await req.text() });
}
