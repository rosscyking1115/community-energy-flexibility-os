import { proxy } from "@/lib/proxy";

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ region: string }> },
) {
  const { region } = await params;
  return proxy(`/v1/tariffs/agile/${encodeURIComponent(region)}`);
}
