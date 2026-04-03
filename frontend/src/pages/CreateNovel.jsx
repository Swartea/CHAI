import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, Loader2 } from 'lucide-react';
import { novelApi } from '../api';

const genres = [
  '玄幻', '都市', '科幻', '悬疑', '言情',
  '武侠', '奇幻', '军事', '历史', '游戏'
];

export default function CreateNovel() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    genre: '玄幻',
    theme: '',
    title: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.theme.trim()) {
      setError('请输入小说主题');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await novelApi.create(form);
      navigate('/writing', { state: { novelId: res.data.id } });
    } catch (err) {
      setError(err.response?.data?.detail || '创建失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-900">创建新小说</h2>
        <p className="text-slate-600 mt-1">配置你的小说项目，系统将自动生成世界观、角色和大纲</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Genre */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">小说类型</label>
          <div className="grid grid-cols-5 gap-2">
            {genres.map((g) => (
              <button
                key={g}
                type="button"
                onClick={() => setForm({ ...form, genre: g })}
                className={`p-3 rounded-lg border text-sm font-medium transition-all ${
                  form.genre === g
                    ? 'border-primary-500 bg-primary-50 text-primary-700'
                    : 'border-slate-200 text-slate-600 hover:border-slate-300'
                }`}
              >
                {g}
              </button>
            ))}
          </div>
        </div>

        {/* Theme */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">小说主题 *</label>
          <input
            type="text"
            value={form.theme}
            onChange={(e) => setForm({ ...form, theme: e.target.value })}
            placeholder="例如：修仙者的星际冒险、穿越古代当王爷..."
            className="w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all"
          />
        </div>

        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">标题（可选）</label>
          <input
            type="text"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            placeholder="留空则自动生成"
            className="w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all"
          />
        </div>

        {/* Error */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 px-4 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 size={20} className="animate-spin" />
              正在生成...
            </>
          ) : (
            <>
              <BookOpen size={20} />
              创建小说项目
            </>
          )}
        </button>
      </form>

      {/* Info */}
      <div className="mt-8 p-4 bg-slate-50 rounded-lg text-sm text-slate-600">
        <p className="font-medium text-slate-700 mb-2">创建后将自动生成：</p>
        <ul className="list-disc list-inside space-y-1">
          <li>完整的世界观设定（地理、政治、文化、历史）</li>
          <li>角色体系（主角、配角、反派）</li>
          <li>故事大纲（三幕式结构）</li>
          <li>章节规划</li>
        </ul>
      </div>
    </div>
  );
}
