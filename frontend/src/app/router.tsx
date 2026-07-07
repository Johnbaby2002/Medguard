import { createBrowserRouter } from "react-router-dom";

import Layout from "../components/Layout";
import LoginPage from "../pages/LoginPage";
import DashboardPage from "../pages/DashboardPage";
import MedicationsPage from "../pages/MedicationsPage";
import SafetyPage from "../pages/SafetyPage";
import ProfilePage from "../pages/ProfilePage";
import RemindersPage from "../pages/RemindersPage";
import ReportsPage from "../pages/ReportsPage";
import SupplementsPage from "../pages/SupplementsPage";
import SubstancesPage from "../pages/SubstancesPage";
export const router = createBrowserRouter([
  {
    path: "/",
    element: <LoginPage />,
  },
  {
    element: <Layout />,
    children: [
      {
        path: "/dashboard",
        element: <DashboardPage />,
      },
      {
        path: "/medications",
        element: <MedicationsPage />,
      },
      {
        path: "/supplements",
        element: <SupplementsPage />,
      },
      {
        path: "/substances",
        element: <SubstancesPage />,
      },
      {
        path: "/safety",
        element: <SafetyPage />,
      },
      {
        path: "/reminders",
        element: <RemindersPage />,
      },
      {
        path: "/profile",
        element: <ProfilePage />,
      },
      {
        path: "/reports",
        element: <ReportsPage />,
      },
    ],
  },
]);