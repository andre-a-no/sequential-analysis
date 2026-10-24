---
description: ক্রমিক বিশ্লেষণ (sequential analysis) ও যেকোনো-সময়-বৈধ অনুমানের পরিভাষা - e-value, e-process, confidence sequence, always-valid p-value, mSPRT, alpha spending, information fraction, ARL, SRM, CUPED, e-BH - সমার্থক শব্দ এবং প্রতিটি বাস্তবায়নকারী sequential-analysis পদ্ধতিসহ।
language: bn
---

# পরিভাষা

> এটি [ইংরেজি পৃষ্ঠার](../../guide/glossary.md) অনুবাদ। এটি এখনও কোনো বাংলাভাষী বিশেষজ্ঞ পর্যালোচনা করেননি; দুটির মধ্যে পার্থক্য থাকলে ইংরেজি পৃষ্ঠাটিই প্রামাণ্য।

ক্রমিক বিশ্লেষণে এবং এই লাইব্রেরিতে ব্যবহৃত পরিভাষা। প্রচলিত সমার্থক শব্দগুলো
বন্ধনীতে দেওয়া হয়েছে।

**ক্রমিক বিশ্লেষণ, Sequential analysis** (sequential testing, sequential inference)।
এমন পরিসংখ্যান যেখানে পর্যবেক্ষণের সংখ্যা আগে থেকে স্থির নয়। প্রতিটি পর্যবেক্ষণ
বা পর্যবেক্ষণের দলের পরে পদ্ধতিটি সিদ্ধান্ত নেয় থামবে না চালিয়ে যাবে। Wald
(1945) এর প্রতিষ্ঠাতা।

**উঁকি দেওয়া, Peeking** (optional stopping, data peeking, continuous monitoring)।
একটি স্থির-নমুনা পরীক্ষা বারবার দেখা এবং তা তাৎপর্যপূর্ণ (significant) হলে
থামা। এটি মিথ্যা-পজিটিভের হার বাড়িয়ে দেয়; দেখুন
[উঁকি দেওয়া](peeking.md)।

**SPRT** (sequential probability ratio test, ক্রমিক সম্ভাবিতা অনুপাত পরীক্ষা,
Wald's test)। এটি দুটি সরল প্রকল্পের (simple hypothesis) লগ সম্ভাবিতা অনুপাত
(log likelihood ratio) জমা করে এবং তা একটি ব্যবধান ছেড়ে গেলে থামে। `SPRT`;
খণ্ডিত (truncated) সংস্করণ `TwoSPRT` (Lorden's 2-SPRT) ও `kiefer_weiss_plan`।
দেখুন [SPRT](sprt.md)।

**গ্রুপ ক্রমিক নকশা, Group sequential design** (interim analyses, group sequential trial)।
কয়েকটি পরিকল্পিত বিশ্লেষণ, প্রতিটির একটি সীমানা। সীমানাগুলো এমনভাবে বেছে নেওয়া হয়
যাতে সামগ্রিক প্রথম প্রকারের ত্রুটি (type I error) alpha হয়।
`group_sequential_design`। দেখুন [ক্লিনিক্যাল ট্রায়াল](clinical-trials.md)।

**আলফা ব্যয় ফাংশন, Alpha spending function** (error spending, Lan–DeMets)।
এটি বলে প্রতিটি তথ্য-ভগ্নাংশ পর্যন্ত প্রথম প্রকারের ত্রুটির কতটা ব্যবহার করে
ফেলা যাবে। O'Brien–Fleming-ধরনের ব্যয় শুরুতে সামান্য খরচ করে, Pocock-ধরনের
ব্যয় সমানভাবে খরচ করে। `spending="obrien-fleming"`, `"pocock"`, ...

**তথ্য-ভগ্নাংশ, Information fraction।** কোনো বিশ্লেষণে পৌঁছানো পরিকল্পিত
পরিসংখ্যানিক তথ্যের (রোগী, ঘটনা) অংশ।

**অসারতার সীমানা, Futility boundary** (non-binding futility)। একটি নিম্ন সীমানা:
এর নিচে প্রভাবের অভাবে থামার সুপারিশ করা হয়। একটি অবন্ধনকারী (non-binding)
সীমানা প্রথম প্রকারের ত্রুটি না বাড়িয়ে উপেক্ষা করা যায়।

**যেকোনো-সময়-বৈধ অনুমান, Anytime-valid inference** (always-valid inference, safe anytime-valid
inference, SAVI)। এমন পরীক্ষা ও ব্যবধান যাদের নিশ্চয়তা একসঙ্গে প্রতিটি নমুনার
আকারে বজায় থাকে, ফলে এগুলো অবিরাম পর্যবেক্ষণ করা যায় এবং যেকোনো কারণে থামানো
যায়।

**e-মান, E-value** (e-variable, betting score)। একটি অ-ঋণাত্মক পরিসংখ্যান যার
প্রত্যাশা শূন্য প্রকল্পের (null hypothesis) অধীনে সর্বোচ্চ 1। বড় e-মান শূন্য
প্রকল্পের বিরুদ্ধে প্রমাণ: এটি 1/alpha ছাড়ালে প্রত্যাখ্যান করলে প্রথম প্রকারের
ত্রুটি সর্বোচ্চ alpha। অনেক পদ্ধতির `log_e_value` আউটপুট।

**e-প্রক্রিয়া, E-process** (test martingale, test supermartingale, wealth process)।
e-মানের একটি অনুক্রম যা থামার সময়ে (stopping time) বৈধ থাকে। শূন্য প্রকল্পের
অধীনে এর চলমান সর্বোচ্চ মান সর্বোচ্চ alpha সম্ভাবনায় 1/alpha অতিক্রম করে
(Ville-এর অসমতা, Ville's inequality)।

**সর্বদা-বৈধ p-মান, Always-valid p-value** (anytime-valid p-value, sequential p-value)।
এমন একটি p-মান যা যেকোনো থামার সময়ে বৈধ। এটি একটি e-প্রক্রিয়ার চলমান সর্বোচ্চ
মানের বিপরীত (inverse)। যেকোনো-সময়-বৈধ পদ্ধতিগুলোর `p_value` আউটপুট।

**আস্থা অনুক্রম, Confidence sequence** (anytime-valid confidence interval,
always-valid confidence interval, time-uniform confidence interval)। ব্যবধানের
একটি অনুক্রম যা অন্তত 1 − alpha সম্ভাবনায় সব নমুনার আকারে একই সঙ্গে প্রকৃত
মান ধারণ করে।
`BettingConfidenceSequence`, `QuantileConfidenceSequence`,
`CatoniConfidenceSequence`, `AsymptoticConfidenceSequence`, এবং অনেক পরীক্ষার
`lower` ও `upper` আউটপুট। দেখুন
[আস্থা অনুক্রম](confidence-sequences.md)।

**mSPRT** (mixture SPRT, মিশ্রণ SPRT, Robbins' mixture)। এমন একটি SPRT যার বিকল্প
প্রকল্প একটি পূর্ব-বণ্টনের (prior) ওপর গড় করা হয়, যা একে প্রতিটি বিকল্পের
বিরুদ্ধে যেকোনো-সময়-বৈধ করে। `NormalMixtureSPRT` (জানা ভেদাঙ্ক), `TMixtureSPRT`
(অজানা ভেদাঙ্ক)।

**বাজি ধরার মাধ্যমে পরীক্ষণ, Testing by betting।** শূন্য প্রকল্পের বিরুদ্ধে বাজি ধরা
একজন জুয়াড়ির সম্পদ হিসেবে e-প্রক্রিয়া গঠন করা। `BettingMeanTest`,
`BettingConfidenceSequence`, `KernelTwoSampleTest`।

**GROW** (growth-rate optimal, বৃদ্ধি-হারে সর্বোত্তম)। বিকল্প প্রকল্পের অধীনে প্রমাণের
প্রত্যাশিত লগ বৃদ্ধি সর্বাধিক করার জন্য বেছে নেওয়া একটি e-মান।
`TwoProportionTest(method="grow")`।

**সার্বজনীন অনুমান, Universal inference।** একটি সম্ভাবিতা অনুপাত থেকে পাওয়া e-মান,
যেখানে বিকল্পটি কেবল অতীত ডেটা থেকে প্রাক্কলিত। এটি অভিযোজিত নকশার (adaptive
design) অধীনেও বৈধ থাকে। `TwoProportionTest(method="universal")`।

**e-BH** (e-Benjamini–Hochberg)। এটি যেকোনো নির্ভরতার অধীনে অনেক e-মানজুড়ে মিথ্যা
আবিষ্কারের হার (false discovery rate) নিয়ন্ত্রণ করে। `MultipleTests`, `e_bh`।

**e-LOND, অনলাইন FDR।** একটি একটি করে সিদ্ধান্ত নেওয়া প্রকল্পের ধারাজুড়ে মিথ্যা
আবিষ্কারের হার নিয়ন্ত্রণ। `OnlineFDR`।

**SRM** (sample ratio mismatch, নমুনা অনুপাতের অমিল)। শাখাগুলোর মধ্যে ট্রাফিকের
পর্যবেক্ষিত ভাগ কনফিগার করা ভাগ থেকে আলাদা, যা পরীক্ষায় একটি বাগের লক্ষণ।
`SampleRatioMismatch`।

**CUPED** (controlled experiments using pre-experiment data, covariate
adjustment, regression adjustment)। পরীক্ষার আগে পরিমাপ করা একটি কোভেরিয়েট
দিয়ে A/B প্রভাবের ভেদাঙ্ক কমায়।
`ABTest(covariate=True)`, `AnytimeLinearModel`।

**অনুপাত মেট্রিক, Ratio metric** (delta method)। এমন একটি মেট্রিক যা প্রতি
ব্যবহারকারী দুটি যোগফলের অনুপাত, যেমন প্রতি সেশনে আয়। `RatioABTest`।

**পরিবর্তন-বিন্দু শনাক্তকরণ, Change-point detection** (change detection, quickest detection,
online anomaly detection)। একটি প্রবাহের বণ্টন বদলানোর অল্প পরেই সতর্কসংকেত
দেওয়া। `CUSUM`, `ShiryaevRoberts`,
`MeanEDetector`, `QuantileEDetector`, `BayesianChangePoint`। দেখুন
[পরিবর্তন শনাক্তকরণ](change-detection.md)।

**ARL** (average run length, গড় রান দৈর্ঘ্য, ARL₀, mean time to false alarm)। কিছুই
না বদলালে একটি মিথ্যা সতর্কসংকেত পর্যন্ত পর্যবেক্ষণের প্রত্যাশিত সংখ্যা।
পরিবর্তন শনাক্তকারীদের মিথ্যা-সতর্কসংকেত নিয়ন্ত্রণ।

**e-শনাক্তকারী, E-detector।** e-প্রক্রিয়া থেকে গঠিত একটি পরিবর্তন শনাক্তকারী, প্রতিটি
সম্ভাব্য পরিবর্তনের সময়ে একটি করে শুরু হয়। একটি অপ্যারামিতিক (nonparametric)
শূন্য প্রকল্পের অধীনে এর ARL নিশ্চিত। `MeanEDetector`, `QuantileEDetector`।

**Kiefer–Weiss সমস্যা।** সর্বোচ্চ নমুনার আকারসহ এমন ক্রমিক পরীক্ষা খুঁজে বের করা
যা বৃহত্তম প্রত্যাশিত নমুনার আকারকে সর্বনিম্ন করে।
`kiefer_weiss_plan`।

**পরিচালন বৈশিষ্ট্য, Operating characteristic।** একটি পরিকল্পনার ত্রুটির সম্ভাবনা ও নমুনার
আকারের বণ্টন, প্রকৃত প্যারামিটারের অপেক্ষক (function) হিসেবে।
`operating_characteristic`।

**চেকপয়েন্ট, Checkpoint।** একটি JSON মান যেখান থেকে একটি রান হুবহু চালিয়ে যায়।
`Run.checkpoint`, `Run.restore`। দেখুন [স্ট্রিমিং](streaming.md)।

**ইতিহাস ডাইজেস্ট, History digest।** একটি রান যে পর্যবেক্ষণগুলো ব্যবহার করেছে
তাদের ওপর একটি SHA-256 হ্যাশ শৃঙ্খল, নিরীক্ষার (audit) জন্য প্রতিটি চেকপয়েন্টে
রাখা হয়।

**নিশ্চয়তা, Guarantee** (`exact`, `asymptotic`, `model`, `approximate`, `none`)।
যে বৈশিষ্ট্যে এই লাইব্রেরির প্রতিটি পদ্ধতি ঘোষণা করে সে কী প্রতিশ্রুতি দেয়।
দেখুন [কোন পদ্ধতি?](../../choosing.md)।
