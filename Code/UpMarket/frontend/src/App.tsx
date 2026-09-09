import { BrowserRouter, Route, Routes } from "react-router-dom";

import Layout from "./components/Layout";
import { AuthProvider } from "./features/auth/AuthContext";
import LoginPage from "./features/auth/LoginPage";
import RegisterPage from "./features/auth/RegisterPage";
import AnalyticsPage from "./features/analytics/AnalyticsPage";
import PlanPage from "./features/billing/PlanPage";
import CampaignsPage from "./features/campaigns/CampaignsPage";
import ChatPage from "./features/customers/ChatPage";
import SalesPage from "./features/customers/SalesPage";
import ProductPage from "./features/products/ProductPage";
import DashboardPage from "./features/stores/DashboardPage";
import StorePage from "./features/stores/StorePage";

export default function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route element={<Layout />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/stores/:id" element={<StorePage />} />
            <Route path="/stores/:id/chat" element={<ChatPage />} />
            <Route path="/stores/:id/sales" element={<SalesPage />} />
            <Route path="/stores/:id/campaigns" element={<CampaignsPage />} />
            <Route path="/stores/:id/analytics" element={<AnalyticsPage />} />
            <Route path="/stores/:id/plan" element={<PlanPage />} />
            <Route path="/products/:id" element={<ProductPage />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
