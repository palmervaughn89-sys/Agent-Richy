'use client';

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TopNav } from '@/components/layout';
import { VideoLesson, QuizCard, BadgeDisplay } from '@/components/kids';
import { KIDS_MODULES, buildBadgesForProgress, formatDuration, getTotalLessons } from '@/lib/kidsData';
import { FREE_VIDEO_MODULES, FREE_VIDEO_LESSONS } from '@/lib/constants';
import type { KidsModule, Lesson } from '@/lib/types';

export default function KidsPage() {
  const [activeTab, setActiveTab] = useState<'modules' | 'active-lesson' | 'badges'>('modules');
  const [selectedModule, setSelectedModule] = useState<KidsModule | null>(null);
  const [selectedLesson, setSelectedLesson] = useState<Lesson | null>(null);
  const [completedLessons, setCompletedLessons] = useState<string[]>([]);
  const [quizScores, setQuizScores] = useState<Record<string, { score: number; total: number }>>({});
  const [isPremium] = useState(false); // TODO: connect to real subscription

  const badges = buildBadgesForProgress(completedLessons);
  const totalLessons = getTotalLessons();
  const progressPct = totalLessons > 0 ? (completedLessons.length / totalLessons) * 100 : 0;

  const canAccessModule = (moduleIndex: number) => isPremium || moduleIndex < FREE_VIDEO_MODULES;
  const canAccessLesson = (moduleIndex: number, lessonIndex: number) =>
    isPremium || (moduleIndex < FREE_VIDEO_MODULES && lessonIndex < FREE_VIDEO_LESSONS);

  const handleCompleteLesson = (lessonId: string) => {
    if (!completedLessons.includes(lessonId)) {
      setCompletedLessons((prev) => [...prev, lessonId]);
    }
  };

  const handleQuizComplete = (lessonId: string, score: number, total: number) => {
    setQuizScores((prev) => ({ ...prev, [lessonId]: { score, total } }));
    if (score >= total * 0.7) { // 70% to pass
      handleCompleteLesson(lessonId);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <TopNav title="Kids Zone 🎓" />

      <div className="flex-1 overflow-y-auto p-4 md:p-6 pb-20 md:pb-6 space-y-6">
        {/* Global progress */}
        <div className="rounded-xl bg-navy-800 border border-navy-700 p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-white">🎯 Your Progress</h3>
            <span className="text-xs text-gold-400 font-bold">{completedLessons.length}/{totalLessons} lessons</span>
          </div>
          <div className="h-3 rounded-full bg-navy-700 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progressPct}%` }}
              transition={{ duration: 1, ease: 'easeOut' }}
              className="h-full rounded-full bg-gradient-to-r from-gold-400 to-gold-600"
            />
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2">
          {[
            { key: 'modules' as const, label: '📚 Modules', count: KIDS_MODULES.length },
            { key: 'active-lesson' as const, label: '🎬 Lesson', disabled: !selectedLesson },
            { key: 'badges' as const, label: '🏆 Badges', count: badges.filter((b) => b.earned).length },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => !tab.disabled && setActiveTab(tab.key)}
              disabled={tab.disabled}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors
                ${activeTab === tab.key
                  ? 'bg-gold-500 text-white shadow-sm'
                  : tab.disabled
                  ? 'bg-navy-800/50 text-gray-600 cursor-not-allowed'
                  : 'bg-navy-800 text-gray-400 border border-navy-700 hover:text-gray-200'
                }`}
            >
              {tab.label}
              {tab.count != null && (
                <span className="ml-1 text-[10px] opacity-70">({tab.count})</span>
              )}
            </button>
          ))}
        </div>

        {/* Modules grid */}
        {activeTab === 'modules' && (
          <div className="space-y-4">
            {KIDS_MODULES.map((mod, moduleIdx) => {
              const locked = !canAccessModule(moduleIdx);
              const modLessons = mod.lessons;
              const modComplete = modLessons.filter((l) => completedLessons.includes(l.lesson_id)).length;
              const modPct = modLessons.length > 0 ? (modComplete / modLessons.length) * 100 : 0;

              return (
                <motion.div
                  key={mod.module_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: moduleIdx * 0.1 }}
                  className={`rounded-xl bg-navy-800 border p-5 ${
                    locked ? 'border-navy-700/50 opacity-60' : 'border-navy-700'
                  }`}
                >
                  <div className="flex items-start gap-3 mb-3">
                    <span className="text-3xl">{mod.icon}</span>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="text-sm font-bold text-white">{mod.title}</h3>
                        {locked && <span className="text-xs bg-navy-700 text-gray-400 px-2 py-0.5 rounded-full">🔒 Premium</span>}
                        {modPct === 100 && <span className="text-xs bg-green-900/40 text-green-400 px-2 py-0.5 rounded-full">✅ Complete</span>}
                      </div>
                      <p className="text-xs text-gray-400 mt-0.5">{mod.description}</p>
                      <p className="text-[10px] text-gray-500 mt-1">Ages {mod.age_range} • {modLessons.length} lessons</p>
                    </div>
                  </div>

                  {/* Module progress */}
                  <div className="h-1.5 rounded-full bg-navy-700 overflow-hidden mb-3">
                    <div className="h-full rounded-full bg-gold-500 transition-all" style={{ width: `${modPct}%` }} />
                  </div>

                  {/* Lessons */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {modLessons.map((lesson, lessonIdx) => {
                      const lessonLocked = !canAccessLesson(moduleIdx, lessonIdx);
                      const isComplete = completedLessons.includes(lesson.lesson_id);
                      return (
                        <button
                          key={lesson.lesson_id}
                          disabled={lessonLocked}
                          onClick={() => {
                            setSelectedModule(mod);
                            setSelectedLesson(lesson);
                            setActiveTab('active-lesson');
                          }}
                          className={`flex items-center gap-2 px-3 py-2 rounded-lg text-left text-xs transition-colors
                            ${lessonLocked
                              ? 'bg-navy-700/30 text-gray-600 cursor-not-allowed'
                              : isComplete
                              ? 'bg-green-900/20 border border-green-800/40 text-green-300 hover:bg-green-900/30'
                              : 'bg-navy-700/50 text-gray-300 hover:bg-navy-700 hover:text-white'
                            }`}
                        >
                          <span className="text-base flex-shrink-0">
                            {lessonLocked ? '🔒' : isComplete ? '✅' : lesson.thumbnail_emoji}
                          </span>
                          <div className="flex-1 min-w-0">
                            <p className="font-medium truncate">{lesson.title}</p>
                            <p className="text-[10px] opacity-60">{formatDuration(lesson.duration_seconds)}</p>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}

        {/* Active lesson view */}
        {activeTab === 'active-lesson' && selectedLesson && selectedModule && (
          <div className="space-y-4">
            <button
              onClick={() => setActiveTab('modules')}
              className="text-xs text-gray-400 hover:text-gold-400 transition-colors"
            >
              ← Back to modules
            </button>

            <VideoLesson
              title={selectedLesson.title}
              description={selectedLesson.description}
              thumbnailEmoji={selectedLesson.thumbnail_emoji}
              videoUrl={selectedLesson.video_url}
              videoType={selectedLesson.video_type}
            />

            {/* Quiz */}
            {selectedLesson.quiz.length > 0 && (
              <div className="space-y-3">
                <h4 className="text-sm font-semibold text-white">📝 Quiz Time!</h4>
                {selectedLesson.quiz.map((q, i) => (
                  <QuizCard
                    key={i}
                    question={q.question}
                    options={q.options.map((opt, j) => ({
                      label: opt,
                      correct: j === q.correct_index,
                    }))}
                    explanation={q.explanation}
                    onAnswer={(correct) => {
                      if (correct) {
                        handleQuizComplete(
                          selectedLesson.lesson_id,
                          (quizScores[selectedLesson.lesson_id]?.score ?? 0) + 1,
                          selectedLesson.quiz.length,
                        );
                      }
                    }}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Badges tab */}
        {activeTab === 'badges' && (
          <BadgeDisplay badges={badges} />
        )}
      </div>
    </div>
  );
}
