import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { FileText, Loader2, Play, Check, Clock } from 'lucide-react';
import { novelApi, chapterApi } from '../api';

export default function Writing() {
  const location = useLocation();
  const [novels, setNovels] = useState([]);
  const [selectedNovel, setSelectedNovel] = useState(location.state?.novelId || null);
  const [chapters, setChapters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [writing, setWriting] = useState(null);

  useEffect(() => {
    novelApi.list()
      .then(res => {
        setNovels(res.data.novels || []);
        if (res.data.novels?.length > 0 && !selectedNovel) {
          setSelectedNovel(res.data.novels[0].id);
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (selectedNovel) {
      loadChapters(selectedNovel);
    }
  }, [selectedNovel]);

  const loadChapters = async (novelId) => {
    try {
      const res = await chapterApi.list(novelId);
      setChapters(res.data.chapters || []);
    } catch (err) {
      console.error(err);
    }
  };

  const handleWrite = async (chapterIndex) => {
    setWriting(chapterIndex);
    try {
      await chapterApi.write({ novel_id: selectedNovel, chapter_index: chapterIndex });
      await loadChapters(selectedNovel);
    } catch (err) {
      console.error(err);
      alert('写作失败: ' + (err.response?.data?.detail || err.message));
    } finally {
      setWriting(null);
    }
  };

  const progress = chapters.length > 0
    ? Math.round((chapters.filter(c => c.status === 'written').length / chapters.length) * 100)
    : 0;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">写作进度</h2>
        <p className="text-slate-600 mt-1">管理章节写作进度</p>
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

      {/* Progress */}
      {chapters.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-slate-900">完成进度</h3>
            <span className="text-2xl font-bold text-primary-600">{progress}%</span>
          </div>
          <div className="w-full bg-slate-200 rounded-full h-3">
            <div
              className="bg-primary-500 h-3 rounded-full transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-sm text-slate-500 mt-2">
            {chapters.filter(c => c.status === 'written').length} / {chapters.length} 章节
          </p>
        </div>
      )}

      {/* Chapters */}
      {loading ? (
        <div className="text-center py-12 text-slate-500">加载中...</div>
      ) : chapters.length > 0 ? (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div className="divide-y divide-slate-100">
            {chapters.map((chapter) => (
              <div key={chapter.index} className="px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    chapter.status === 'written'
                      ? 'bg-green-100 text-green-600'
                      : 'bg-slate-100 text-slate-400'
                  }`}>
                    {chapter.status === 'written' ? <Check size={16} /> : <span>{chapter.index + 1}</span>}
                  </div>
                  <div>
                    <p className="font-medium text-slate-900">{chapter.title}</p>
                    <p className="text-sm text-slate-500">
                      {chapter.word_count > 0 ? `${chapter.word_count} 字` : '待写作'}
                    </p>
                  </div>
                </div>

                {chapter.status === 'pending' && (
                  <button
                    onClick={() => handleWrite(chapter.index)}
                    disabled={writing !== null}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50 transition-colors flex items-center gap-2"
                  >
                    {writing === chapter.index ? (
                      <>
                        <Loader2 size={16} className="animate-spin" />
                        写作中...
                      </>
                    ) : (
                      <>
                        <Play size={16} />
                        开始写作
                      </>
                    )}
                  </button>
                )}

                {chapter.status === 'written' && (
                  <span className="text-sm text-green-600 flex items-center gap-1">
                    <Check size={16} />
                    已完成
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      ) : selectedNovel ? (
        <div className="text-center py-12 text-slate-500">
          该小说暂无章节数据
        </div>
      ) : (
        <div className="text-center py-12 text-slate-500">
          请先创建小说
        </div>
      )}
    </div>
  );
}
