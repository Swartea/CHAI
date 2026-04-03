import { useState } from 'react';
import { FlaskConical, Loader2, Search, BookOpen } from 'lucide-react';
import { deconstructApi } from '../api';

export default function Deconstruct() {
  const [form, setForm] = useState({
    entry_name: '',
    entry_id: '',
    genre: '',
    max_books: 5,
  });
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [templates, setTemplates] = useState([]);

  const handleSearch = async () => {
    if (!form.entry_name && !form.entry_id) {
      setError('请输入词条名称或ID');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await deconstructApi.run(form);
      setResults(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || '拆书失败');
    } finally {
      setLoading(false);
    }
  };

  const loadTemplates = async () => {
    try {
      const res = await deconstructApi.listTemplates(form.genre);
      setTemplates(res.data.templates || []);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">拆书分析</h2>
        <p className="text-slate-600 mt-1">从番茄小说热词榜抓取热门书籍，AI 自动拆解结构</p>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h3 className="font-semibold text-slate-900 mb-4">搜索词条</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">词条名称</label>
            <input
              type="text"
              value={form.entry_name}
              onChange={(e) => setForm({ ...form, entry_name: e.target.value })}
              placeholder="例如：都市脑洞、玄幻奇幻"
              className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">词条 ID</label>
            <input
              type="text"
              value={form.entry_id}
              onChange={(e) => setForm({ ...form, entry_id: e.target.value })}
              placeholder="番茄热词榜 ID"
              className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">类型</label>
            <select
              value={form.genre}
              onChange={(e) => setForm({ ...form, genre: e.target.value })}
              className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none"
            >
              <option value="">不限</option>
              <option value="玄幻">玄幻</option>
              <option value="都市">都市</option>
              <option value="科幻">科幻</option>
              <option value="悬疑">悬疑</option>
              <option value="言情">言情</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">抓取数量</label>
            <input
              type="number"
              min="1"
              max="20"
              value={form.max_books}
              onChange={(e) => setForm({ ...form, max_books: parseInt(e.target.value) })}
              className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none"
            />
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        <button
          onClick={handleSearch}
          disabled={loading}
          className="px-6 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50 transition-colors flex items-center gap-2"
        >
          {loading ? <Loader2 size={18} className="animate-spin" /> : <Search size={18} />}
          {loading ? '抓取中...' : '抓取并拆解'}
        </button>
      </div>

      {/* Results */}
      {results && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h3 className="font-semibold text-slate-900 mb-4">
            拆解结果 ({results.books_analyzed} 本书)
          </h3>

          <div className="space-y-4">
            {results.results?.map((result, idx) => (
              <div key={idx} className="p-4 bg-slate-50 rounded-lg">
                <div className="flex items-start gap-3">
                  <BookOpen size={20} className="text-primary-600 mt-1" />
                  <div className="flex-1">
                    <h4 className="font-medium text-slate-900">{result.book_title}</h4>
                    <p className="text-sm text-slate-600 mt-1">{result.summary}</p>

                    {result.characters && (
                      <div className="mt-3">
                        <p className="text-sm font-medium text-slate-700">角色模板：</p>
                        <p className="text-sm text-slate-600">{result.characters.length} 个角色</p>
                      </div>
                    )}

                    {result.plot_patterns && (
                      <div className="mt-2">
                        <p className="text-sm font-medium text-slate-700">情节模式：</p>
                        <p className="text-sm text-slate-600">{result.plot_patterns.join(', ')}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Templates */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-slate-900">已存储的模板</h3>
          <button
            onClick={loadTemplates}
            className="text-sm text-primary-600 hover:text-primary-700"
          >
            刷新
          </button>
        </div>

        {templates.length > 0 ? (
          <div className="space-y-2">
            {templates.map((t) => (
              <div key={t.id} className="p-3 bg-slate-50 rounded-lg text-sm">
                <p className="font-medium text-slate-900">{t.book_title}</p>
                <p className="text-slate-500 text-xs">{t.genre}</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-slate-500 text-sm">暂无存储的模板</p>
        )}
      </div>
    </div>
  );
}
