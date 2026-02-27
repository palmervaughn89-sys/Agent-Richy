import type { MetadataRoute } from 'next';

export default function sitemap(): MetadataRoute.Sitemap {
  const base = 'https://agent-richy-pwgx.vercel.app';
  const lastModified = new Date();

  return [
    { url: base, lastModified, changeFrequency: 'weekly', priority: 1.0 },
    { url: `${base}/chat`, lastModified, changeFrequency: 'weekly', priority: 0.9 },
    { url: `${base}/dashboard`, lastModified, changeFrequency: 'weekly', priority: 0.8 },
    { url: `${base}/calculators`, lastModified, changeFrequency: 'monthly', priority: 0.7 },
    { url: `${base}/kids`, lastModified, changeFrequency: 'monthly', priority: 0.7 },
    { url: `${base}/profile`, lastModified, changeFrequency: 'monthly', priority: 0.6 },
    { url: `${base}/plan`, lastModified, changeFrequency: 'monthly', priority: 0.6 },
    { url: `${base}/lifestyle-portfolio`, lastModified, changeFrequency: 'monthly', priority: 0.5 },
    { url: `${base}/upgrade`, lastModified, changeFrequency: 'monthly', priority: 0.4 },
  ];
}
