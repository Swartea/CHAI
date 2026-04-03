import { useState } from 'react';
import { Download, FileText, BookOpen, File, Loader2 } from 'lucide-react';
import { novelApi } from '../api';

const formats = [
  { id: 'markdown', label: 'Markdown', icon: FileText, desc: '.md 格式，适合写作和编辑' },
  { id: 'epub', label: 'EPUB', icon: BookOpen, desc: '电子书格式，适合阅读器' },
  { id: 'pdf', label: 'PDF', icon: File, desc: 'PDF 格式，适合打印和分享' },
];

export default function Export() {
  const [novels, setNovels] = useState([]);
  const [selectedNovel, setSelectedNovel] = useState(null);
  const [format, setFormat] = useState('markdown');
  const [loading, setLoading] = useState(false);
  const [exported, setExported] = useState(false);

  useState(() => {
    novelApi.list()
      .then(res => {
        setNovels(res.data.novels || []);
        if (res.data.novels?.length > 0) {
          setSelectedNovel(res.data.novels[0].id);
        }
      })
      .catch(console.error);
  }, []);

  const handleExport = async () => {
    if (!selectedNovel) return;

    setLoading(true);
    setExported(false);

    // Simulate export
    await new Promise(resolve => setTimeout(resolve, 1500));

    setLoading(false);
    setExported(true);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">导出小说</h2>
        <p className="text-slate-600 mt-1">将小说导出为不同格式</p>
      </div>

      {/* Novel Selector */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <label className="block text-sm font-medium text-slate-700 mb-2">选择小说</label>
        <select
          value={selectedNovel || ''}
          onChange={(e) => setSelectedNovel(e.target.value)}
          className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:border-primary-500 outline-none"
        >
          {novels.length === 0 && <option value="">暂无小说</option>}
          {novels.map(n => (
            <option key={n.id} value={n.id}>{n.title || n.id}</option>
          ))}
        </select>
      </div>

      {/* Format Selector */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <label className="block text-sm font-medium text-slate-700 mb-3">导出格式</label>
        <div className="grid grid-cols-3 gap-4">
          {formats.map((f) => (
            <button
              key={f.id}
              onClick={() => setFormat(f.id)}
              className={`p-4 rounded-lg border-2 text-left transition-all ${
                format === f.id
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-slate-200 hover:border-slate-300'
              }`}
            >
              <f.icon size={24} className={format === f.id ? 'text-primary-600' : 'text-slate-400'} />
              <p className={`font-medium mt-2 ${format === f.id ? 'text-primary-700' : 'text-slate-900'}`}>
                {f.label}
              </p>
              <p className="text-xs text-slate-500 mt-1">{f.desc}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Export Button */}
      <button
        onClick={handleExport}
        disabled={!selectedNovel || loading}
        className="w-full py-3 px-4 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <Loader2 size={20} className="animate-spin" />
            导出中...
          </>
        ) : (
          <>
            <Download size={20} />
            导出 {formats.find(f => f.id === format)?.label}
          </>
        )}
      </button>

      {/* Success Message */}
      {exported && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
          导出成功！文件已保存到 output 目录。
        </div>
      )}
    </div>
  );
}
