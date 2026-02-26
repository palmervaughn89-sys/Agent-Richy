import { NextResponse } from 'next/server';
import { KIDS_MODULES, MODULE_BADGES, MEGA_BADGE, getTotalLessons } from '@/lib/kidsData';

export async function GET() {
  return NextResponse.json({
    modules: KIDS_MODULES,
    badges: MODULE_BADGES,
    mega_badge: MEGA_BADGE,
    total_lessons: getTotalLessons(),
  });
}
