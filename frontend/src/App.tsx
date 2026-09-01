import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { NewQuery } from './pages/NewQuery';
import { QueryHistory } from './pages/QueryHistory';
import { DecisionResolved } from './pages/DecisionResolved';
import { DecisionUnresolved } from './pages/DecisionUnresolved';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="query/new" element={<NewQuery />} />
          <Route path="query/:id/resolved" element={<DecisionResolved />} />
          <Route path="query/:id/unresolved" element={<DecisionUnresolved />} />
          <Route path="history" element={<QueryHistory />} />
          {/* Fallback for unused links */}
          <Route path="knowledge" element={<div className="p-8">Knowledge Base Placeholder</div>} />
          <Route path="audit" element={<div className="p-8">Audit Trail Placeholder</div>} />
          <Route path="settings" element={<div className="p-8">Settings Placeholder</div>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
