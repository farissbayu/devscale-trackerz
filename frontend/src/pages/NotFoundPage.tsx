import { Link } from "react-router-dom";

import { EmptyState } from "../components/ui";

export function NotFoundPage() {
  return (
    <div className="space-y-4">
      <EmptyState title="Page not found" description="The page you are looking for does not exist." />
      <div className="text-center">
        <Link to="/" className="text-sm font-medium text-indigo-600 hover:text-indigo-700">
          Back to dashboard
        </Link>
      </div>
    </div>
  );
}
