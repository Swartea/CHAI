import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Home, BookOpen, Globe, Users, FileText, Download, FlaskConical } from 'lucide-react';

import Dashboard from './pages/Dashboard';
import CreateNovel from './pages/CreateNovel';
import Deconstruct from './pages/Deconstruct';
import WorldView from './pages/WorldView';
import Writing from './pages/Writing';
import Export from './pages/Export';

const navItems = [
  { path: '/', icon: Home, label: '总览' },
  { path: '/create', icon: BookOpen, label: '创建小说' },
  { path: '/deconstruct', icon: FlaskConical, label: '拆书分析' },
  { path: '/world', icon: Globe, label: '世界观' },
  { path: '/writing', icon: FileText, label: '写作进度' },
  { path: '/export', icon: Download, label: '导出' },
];

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-slate-200">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold text-primary-600">CHAI</h1>
              <span className="text-sm text-slate-500">AI 小说自动化写作系统</span>
            </div>
          </div>
        </header>

        {/* Navigation */}
        <nav className="bg-white border-b border-slate-200">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex gap-1">
              {navItems.map((item) => (
                <NavLink key={item.path} {...item} />
              ))}
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/create" element={<CreateNovel />} />
            <Route path="/deconstruct" element={<Deconstruct />} />
            <Route path="/world" element={<WorldView />} />
            <Route path="/writing" element={<Writing />} />
            <Route path="/export" element={<Export />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

function NavLink({ path, icon: Icon, label }) {
  const location = useLocation();
  const isActive = location.pathname === path;

  return (
    <Link
      to={path}
      className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
        isActive
          ? 'border-primary-500 text-primary-600'
          : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
      }`}
    >
      <Icon size={18} />
      {label}
    </Link>
  );
}

export default App;
