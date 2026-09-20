import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";
import ActionCard from "../components/ActionCard";
import { QueryError } from "../components/Insights";

export default function Actions() {
  const q = useQuery({ queryKey: ["actions", "all"], queryFn: () => api.actions() });
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">All recommended actions (ranked by expected tonnes)</h2>
      <QueryError error={q.error} what="actions" />
      <div className="grid gap-3 md:grid-cols-2">{q.data?.map((a) => <ActionCard key={a.id} a={a} />)}</div>
    </div>
  );
}
