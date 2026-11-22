import { Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { CurriculumPage } from "./pages/CurriculumPage";
import { DashboardPage } from "./pages/DashboardPage";
import { HistoryPage } from "./pages/HistoryPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { ProgressPage } from "./pages/ProgressPage";
import { SessionPage } from "./pages/SessionPage";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<DashboardPage />} />
        <Route path="curriculum" element={<CurriculumPage />} />
        <Route path="sessions/:sessionId" element={<SessionPage />} />
        <Route path="history" element={<HistoryPage />} />
        <Route path="progress" element={<ProgressPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
