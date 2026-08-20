import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css";
import Topbar from "./components/Topbar";
import Sidebar from "./components/Sidebar";
import Footer from "./components/Footer";
import Dashboard from "./pages/Dashboard";
import Forecast from "./pages/Forecast";
import ModelAnalysis from "./pages/ModelAnalysis";
import Methodology from "./pages/Methodology";

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Topbar />
        <div className="app-body">
          <Sidebar />
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/forecast" element={<Forecast />} />
            <Route path="/model-analysis" element={<ModelAnalysis />} />
            <Route path="/methodology" element={<Methodology />} />
          </Routes>
        </div>
        <Footer />
      </div>
    </BrowserRouter>
  );
}
