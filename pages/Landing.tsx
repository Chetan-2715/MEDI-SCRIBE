import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Activity, Camera, Shield, FileText, Calendar, Clock, ArrowRight } from 'lucide-react';
import { ThemeToggle } from '../components/ThemeToggle';
import { useAuth } from '../context/AuthContext';

const Landing: React.FC = () => {
    const navigate = useNavigate();
    const { isAuthenticated } = useAuth();

    const handleStart = () => {
        if (isAuthenticated) {
            navigate('/dashboard');
        } else {
            navigate('/login');
        }
    };

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1
            }
        }
    };

    const itemVariants = {
        hidden: { y: 20, opacity: 0 },
        visible: {
            y: 0,
            opacity: 1,
            transition: {
                type: "spring",
                stiffness: 100
            }
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-950 transition-colors duration-300">
            {/* Header */}
            <header className="fixed w-full bg-white/80 dark:bg-slate-900/80 backdrop-blur-md z-50 border-b border-slate-200 dark:border-slate-800">
                <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-teal-600 rounded-lg flex items-center justify-center text-white">
                            <Activity size={20} />
                        </div>
                        <span className="text-xl font-bold text-slate-900 dark:text-white">Medi-Scribe</span>
                    </div>

                    <div className="flex items-center gap-4">
                        <ThemeToggle />
                        {!isAuthenticated && (
                            <button
                                onClick={handleStart}
                                className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-teal-600 dark:hover:text-teal-400 transition-colors hidden md:block"
                            >
                                Sign In
                            </button>
                        )}
                        <button
                            onClick={handleStart}
                            className="bg-teal-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-teal-700 transition-all shadow-lg shadow-teal-600/20"
                        >
                            Get Started
                        </button>
                    </div>
                </div>
            </header>

            {/* Hero Section */}
            <section className="pt-32 pb-20 px-6">
                <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-12 items-center">
                    <motion.div
                        initial="hidden"
                        animate="visible"
                        variants={containerVariants}
                    >
                        <motion.div variants={itemVariants} className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-50 dark:bg-teal-900/30 text-teal-600 dark:text-teal-400 text-xs font-semibold mb-6">
                            <span className="w-2 h-2 rounded-full bg-teal-600 animate-pulse"></span>
                            AI-Powered Healthcare Assistant
                        </motion.div>

                        <motion.h1 variants={itemVariants} className="text-5xl lg:text-7xl font-bold text-slate-900 dark:text-white leading-tight mb-6">
                            Your Health, <br />
                            <span className="text-transparent bg-clip-text bg-linear-to-r from-teal-600 to-cyan-500">
                                Simply Understood
                            </span>
                        </motion.h1>

                        <motion.p variants={itemVariants} className="text-lg text-slate-600 dark:text-slate-400 mb-8 max-w-lg leading-relaxed">
                            Decipher complex prescriptions instantly using advanced AI. Get reminders, understand medicines, and take control of your well-being.
                        </motion.p>

                        <motion.div variants={itemVariants} className="flex gap-4">
                            <button
                                onClick={handleStart}
                                className="bg-teal-600 text-white px-8 py-4 rounded-xl font-bold text-lg hover:bg-teal-700 transition-all shadow-xl shadow-teal-600/30 flex items-center gap-2 group"
                            >
                                Try Medi-Scribe
                                <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                            </button>

                        </motion.div>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.8 }}
                        className="relative"
                    >
                        <div className="absolute inset-0 bg-linear-to-tr from-teal-200 to-cyan-200 dark:from-teal-900/20 dark:to-cyan-900/20 rounded-full blur-3xl opacity-50 animate-pulse"></div>
                        <div className="relative bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-slate-100 dark:border-slate-800 p-6">
                            {/* Mock UI Card */}
                            <div className="flex items-center gap-4 mb-6 border-b border-slate-100 dark:border-slate-800 pb-4">
                                <div className="w-12 h-12 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center">
                                    <FileText className="text-teal-600" />
                                </div>
                                <div>
                                    <div className="h-4 w-32 bg-slate-200 dark:bg-slate-700 rounded mb-2"></div>
                                    <div className="h-3 w-20 bg-slate-100 dark:bg-slate-800 rounded"></div>
                                </div>
                            </div>
                            <div className="space-y-3">
                                {[1, 2, 3].map(i => (
                                    <div key={i} className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                                        <div className="flex items-center gap-3">
                                            <div className="w-8 h-8 rounded-full bg-teal-100 dark:bg-teal-900/30 flex items-center justify-center text-teal-600">
                                                <Clock size={16} />
                                            </div>
                                            <div>
                                                <div className="h-3 w-24 bg-slate-200 dark:bg-slate-700 rounded mb-1"></div>
                                                <div className="h-2 w-16 bg-slate-100 dark:bg-slate-800 rounded"></div>
                                            </div>
                                        </div>
                                        <div className="h-6 w-12 bg-teal-100 dark:bg-teal-900 rounded-full"></div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </motion.div>
                </div>
            </section>

            {/* Features Section */}
            <section className="py-20 bg-white dark:bg-slate-900 transition-colors duration-300">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl lg:text-4xl font-bold text-slate-900 dark:text-white mb-4">Why Medi-Scribe?</h2>
                        <p className="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
                            We verify and digitize your medical records with precision, ensuring you never miss a dose or misunderstand a diagnosis.
                        </p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        <FeatureCard
                            icon={Camera}
                            title="Instant OCR"
                            desc="Deep analysis of handwriting to extract structured data from prescriptions in seconds."
                            delay={0.1}
                        />
                        <FeatureCard
                            icon={Shield}
                            title="Secure & Private"
                            desc="Your health data is encrypted and stored safely. We prioritize your privacy above all."
                            delay={0.2}
                        />
                        <FeatureCard
                            icon={Calendar}
                            title="Smart Reminders"
                            desc="Automatically schedule doses on your Google Calendar so you never miss a pill."
                            delay={0.3}
                        />
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-8 text-center text-slate-500 dark:text-slate-400 text-sm border-t border-slate-200 dark:border-slate-800">
                <p>&copy; 2024 Medi-Scribe. All rights reserved.</p>
            </footer>
        </div>
    );
};

const FeatureCard = ({ icon: Icon, title, desc, delay }: any) => {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay }}
            className="p-8 rounded-2xl bg-slate-50 dark:bg-slate-800 hover:shadow-xl transition-shadow border border-transparent hover:border-teal-100 dark:hover:border-teal-900 group"
        >
            <div className="w-14 h-14 bg-white dark:bg-slate-900 rounded-xl flex items-center justify-center text-teal-600 shadow-sm mb-6 group-hover:scale-110 transition-transform">
                <Icon size={28} />
            </div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">{title}</h3>
            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                {desc}
            </p>
        </motion.div>
    );
};

export default Landing;
