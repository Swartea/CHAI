import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Globe, Users, FileText, FlaskConical, ArrowRight } from 'lucide-react';
import { getStatus, novelApi } from '../api';

const stats = [
  { label: '小说项目', icon: BookOpen, key: 'novels', color: 'text-blue-600' },
  { label: '世界观设定', icon: Globe, key: 'worlds', color: 'text-green-600' },
  { label: '章节完成', icon: FileText, key: 'chapters', color: 'text-purple-600' },
  { label: '拆书模板', icon: FlaskConical, key: 'templates', color: 'text-orange-600' },
];

export default function Dashboard() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getStatus()
      .then(res => setStatus(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const quickActions = [
    { label: '创建新小说', to: '/create', desc: '开始一个新的写作项目' },
    { label: '拆书分析', to: '/deconstruct', desc: '从番茄热词榜拆解热门书籍' },
    { label: '查看世界观', to: '/world', desc: '浏览和管理世界观设定' },
    { label: '继续写作', to: '/writing', desc: '查看写作进度' },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">欢迎使用 CHAI</h2>
        <p className="text-slate-600 mt-1">AI 小说自动化写作系统，让创作更高效</p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {quickActions.map((action) => (
          <Link
            key={action.to}
            to={action.to}
            className="group p-6 bg-white rounded-xl shadow-sm border border-slate-200 hover:shadow-md hover:border-primary-300 transition-all"
          >
            <h3 className="font-semibold text-slate-900 group-hover:text-primary-600 transition-colors">
              {action.label}
            </h3>
            <p className="text-sm text-slate-500 mt-1">{action.desc}</p>
            <ArrowRight size={18} className="mt-3 text-slate-400 group-hover:text-primary-500 group-hover:translate-x-1 transition-all" />
          </Link>
        ))}
      </div>

      {/* Status Cards */}
      <div>
        <h3 className="text-lg font-semibold text-slate-900 mb-4">系统状态</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {stats.map((stat) => (
            <div key={stat.label} className="p-4 bg-white rounded-lg border border-slate-200">
              <div className={`flex items-center gap-2 ${stat.color}`}>
                <stat.icon size={20} />
                <span className="text-sm font-medium">{stat.label}</span>
              </div>
              <p className="text-2xl font-bold text-slate-900 mt-2">
                {loading ? '-' : status?.projects?.length || 0}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Projects */}
      <div>
        <h3 className="text-lg font-semibold text-slate-900 mb-4">最近项目</h3>
        <div className="bg-white rounded-lg border border-slate-200">
          {loading ? (
            <div className="p-8 text-center text-slate-500">加载中...</div>
          ) : status?.projects?.length > 0 ? (
            <div className="divide-y divide-slate-100">
              {status.projects.slice(0, 5).map((project) => (
                <div key={project} className="p-4 flex items-center justify-between">
                  <div>
                    <p className="font-medium text-slate-900">{project}</p>
                  </div>
                  <Link to="/writing" className="text-primary-600 hover:text-primary-700 text-sm">
                    查看
                  </Link>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center">
              <p className="text-slate-500">暂无项目</p>
              <Link to="/create" className="text-primary-600 hover:text-primary-700 text-sm mt-2 inline-block">
                创建第一个小说
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
