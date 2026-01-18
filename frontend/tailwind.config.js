/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				surface: {
					primary: '#FFFFFF',
					secondary: '#F5F5F7',
					tertiary: '#E8E8ED',
					elevated: 'rgba(255, 255, 255, 0.72)'
				},
				label: {
					primary: '#1D1D1F',
					secondary: '#86868B',
					tertiary: '#AEAEB2'
				},
				fill: {
					primary: 'rgba(120, 120, 128, 0.2)',
					secondary: 'rgba(120, 120, 128, 0.16)',
					tertiary: 'rgba(118, 118, 128, 0.12)'
				},
				accent: {
					blue: '#0071E3',
					'blue-hover': '#0077ED',
					green: '#30D158',
					orange: '#FF9F0A',
					red: '#FF453A',
					purple: '#BF5AF2'
				},
				separator: 'rgba(60, 60, 67, 0.12)'
			},
			fontFamily: {
				sf: [
					'SF Pro Display',
					'-apple-system',
					'BlinkMacSystemFont',
					'Helvetica Neue',
					'Arial',
					'sans-serif'
				]
			},
			fontSize: {
				'title-1': ['28px', { lineHeight: '34px', fontWeight: '700', letterSpacing: '-0.016em' }],
				'title-2': ['22px', { lineHeight: '28px', fontWeight: '700', letterSpacing: '-0.016em' }],
				'title-3': ['20px', { lineHeight: '25px', fontWeight: '600', letterSpacing: '-0.012em' }],
				'headline': ['17px', { lineHeight: '22px', fontWeight: '600', letterSpacing: '-0.01em' }],
				'body': ['17px', { lineHeight: '22px', fontWeight: '400', letterSpacing: '-0.01em' }],
				'callout': ['16px', { lineHeight: '21px', fontWeight: '400', letterSpacing: '-0.01em' }],
				'subhead': ['15px', { lineHeight: '20px', fontWeight: '400', letterSpacing: '-0.01em' }],
				'footnote': ['13px', { lineHeight: '18px', fontWeight: '400', letterSpacing: '-0.006em' }],
				'caption-1': ['12px', { lineHeight: '16px', fontWeight: '400' }],
				'caption-2': ['11px', { lineHeight: '13px', fontWeight: '400' }]
			},
			borderRadius: {
				'apple-sm': '8px',
				'apple': '12px',
				'apple-lg': '18px',
				'apple-xl': '22px'
			},
			boxShadow: {
				'subtle': '0 0.5px 0 0 rgba(0, 0, 0, 0.05)',
				'card': '0 0 0 0.5px rgba(0, 0, 0, 0.03), 0 2px 8px rgba(0, 0, 0, 0.04), 0 8px 24px rgba(0, 0, 0, 0.06)',
				'elevated': '0 0 0 0.5px rgba(0, 0, 0, 0.05), 0 4px 16px rgba(0, 0, 0, 0.08), 0 16px 48px rgba(0, 0, 0, 0.1)'
			},
			backdropBlur: {
				'apple': '20px'
			},
			animation: {
				'fade-in': 'fadeIn 0.25s ease-out',
				'slide-up': 'slideUp 0.35s cubic-bezier(0.4, 0, 0.2, 1)',
				'scale-up': 'scaleUp 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
				'progress': 'progress 1.5s ease-in-out infinite'
			},
			keyframes: {
				fadeIn: {
					from: { opacity: '0' },
					to: { opacity: '1' }
				},
				slideUp: {
					from: { opacity: '0', transform: 'translateY(8px)' },
					to: { opacity: '1', transform: 'translateY(0)' }
				},
				scaleUp: {
					from: { opacity: '0', transform: 'scale(0.98)' },
					to: { opacity: '1', transform: 'scale(1)' }
				},
				progress: {
					'0%': { transform: 'translateX(-100%)' },
					'100%': { transform: 'translateX(100%)' }
				}
			},
			transitionTimingFunction: {
				'apple': 'cubic-bezier(0.4, 0, 0.2, 1)'
			}
		}
	},
	plugins: []
};
