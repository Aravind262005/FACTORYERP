import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { NewQuery } from './pages/NewQuery';
import { QueryHistory } from './pages/QueryHistory';
import { DecisionResolved } from './pages/DecisionResolved';
import { DecisionUnresolved } from './pages/DecisionUnresolved';
import { KnowledgeBase } from './pages/KnowledgeBase';

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
          <Route path="knowledge" element={<KnowledgeBase />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
