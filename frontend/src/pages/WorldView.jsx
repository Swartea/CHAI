import { useState, useEffect } from 'react';
import { Globe, ChevronRight, ChevronDown, Map, Building, BookOpen, History, Users } from 'lucide-react';
import { novelApi, worldApi } from '../api';

const categoryIcons = {
  geography: Map,
  politics: Building,
  culture: BookOpen,
  history: History,
  social: Users,
};

const categoryLabels = {
  geography: '地理',
  politics: '政治',
  culture: '文化',
  history: '历史',
  social: '社会',
};

export default function WorldView() {
  const [novels, setNovels] = useState([]);
  const [selectedNovel, setSelectedNovel] = useState(null);
  const [world, setWorld] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState({});

  useEffect(() => {
    novelApi.list()
      .then(res => {
        setNovels(res.data.novels || []);
        if (res.data.novels?.length > 0) {
          setSelectedNovel(res.data.novels[0].id);
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (selectedNovel) {
      worldApi.get(selectedNovel)
        .then(res => setWorld(res.data))
        .catch(console.error);
    }
  }, [selectedNovel]);

  const toggleCategory = (cat) => {
    setExpanded(prev => ({ ...prev, [cat]: !prev[cat] }));
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">世界观浏览</h2>
        <p className="text-slate-600 mt-1">查看和管理小说世界观设定</p>
      </div>

      {/* Novel Selector */}
      <div className="bg-white rounded-xl border border-slate-200 p-4">
        <label className="block text-sm font-medium text-slate-700 mb-2">选择小说</label>
        <select
          value={selectedNovel || ''}
          onChange={(e) => setSelectedNovel(e.target.value)}
          className="w-full md:w-64 px-3 py-2 rounded-lg border border-slate-300 focus:border-primary-500 outline-none"
        >
          {novels.length === 0 && <option value="">暂无小说</option>}
          {novels.map(n => (
            <option key={n.id} value={n.id}>{n.title || n.id}</option>
          ))}
        </select>
      </div>

      {/* World Display */}
      {loading ? (
        <div className="text-center py-12 text-slate-500">加载中...</div>
      ) : world ? (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          {/* Header */}
          <div className="p-6 border-b border-slate-200">
            <div className="flex items-center gap-3">
              <Globe size={28} className="text-primary-600" />
              <div>
                <h3 className="text-xl font-bold text-slate-900">{world.name || selectedNovel}</h3>
                <p className="text-sm text-slate-500">{world.genre}</p>
              </div>
            </div>
          </div>

          {/* Categories */}
          <div className="divide-y divide-slate-100">
            {Object.entries(categoryLabels).map(([key, label]) => {
              const Icon = categoryIcons[key];
              const data = world[key];
              const isExpanded = expanded[key];

              if (!data) return null;

              return (
                <div key={key}>
                  <button
                    onClick={() => toggleCategory(key)}
                    className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <Icon size={20} className="text-slate-400" />
                      <span className="font-medium text-slate-900">{label}</span>
                    </div>
                    {isExpanded ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
                  </button>

                  {isExpanded && (
                    <div className="px-6 pb-4">
                      <div className="bg-slate-50 rounded-lg p-4">
                        {typeof data === 'object' ? (
                          <pre className="text-sm text-slate-700 whitespace-pre-wrap font-sans">
                            {JSON.stringify(data, null, 2)}
                          </pre>
                        ) : (
                          <p className="text-sm text-slate-700">{data}</p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="text-center py-12 text-slate-500">
          {selectedNovel ? '该小说暂无世界观数据' : '请选择一部小说'}
        </div>
      )}
    </div>
  );
}
