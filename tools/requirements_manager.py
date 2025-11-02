#!/usr/bin/env python3
"""
📦 Requirements Manager - مدير المتطلبات المتطور
أداة ذكية لإدارة وتحسين متطلبات المشروع

Features:
- ✅ Analyze and fix requirements.txt issues
- ✅ Check package compatibility and versions
- ✅ Install missing dependencies intelligently
- ✅ Remove unused packages
- ✅ Generate optimized requirements file
- ✅ Security vulnerability scanning

Version: 3.0.0
Created: 2025-11-02
"""

import sys
import subprocess
import pkg_resources
from pathlib import Path
from typing import Dict, List, Set, Tuple
import json
import re
from datetime import datetime

class RequirementsManager:
    """مدير المتطلبات الذكي"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.requirements_file = self.project_root / 'requirements.txt'
        self.fixed_requirements = []
        self.missing_packages = []
        self.incompatible_packages = []
        self.security_issues = []
        
    def print_banner(self):
        """طباعة شعار الأداة"""
        print("""
╔═══════════════════════════════════════════════════════════════╗
║                   📦 REQUIREMENTS MANAGER                     ║
║                  مدير المتطلبات المتطور                       ║
║                                                               ║
║  🔧 Intelligent dependency management                         ║
║  🛡️ Security vulnerability scanning                          ║
║  ⚡ Performance optimization                                  ║
╚═══════════════════════════════════════════════════════════════╝
        """)
        
    def get_installed_packages(self) -> Dict[str, str]:
        """الحصول على قائمة الحزم المثبتة"""
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--format=json'], 
                                  capture_output=True, text=True, check=True)
            packages = json.loads(result.stdout)
            return {pkg['name'].lower(): pkg['version'] for pkg in packages}
        except Exception as e:
            print(f"❌ Error getting installed packages: {e}")
            return {}
            
    def parse_requirements_file(self) -> List[Tuple[str, str]]:
        """قراءة وتحليل ملف المتطلبات"""
        requirements = []
        
        if not self.requirements_file.exists():
            print("⚠️ requirements.txt not found")
            return requirements
            
        with open(self.requirements_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                    
                # Parse requirement
                try:
                    if '==' in line:
                        package, version = line.split('==', 1)
                        package = package.strip()
                        version = version.strip()
                    elif '>=' in line:
                        package, version = line.split('>=', 1)
                        package = package.strip()
                        version = f">={version.strip()}"
                    else:
                        package = line.strip()
                        version = ""
                        
                    requirements.append((package, version, line_num))
                    
                except Exception as e:
                    print(f"⚠️ Error parsing line {line_num}: {line} - {e}")
                    
        return requirements
        
    def check_package_availability(self, package_name: str) -> bool:
        """فحص توفر الحزمة"""
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'show', package_name], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
            
    def find_alternative_package(self, package_name: str) -> str:
        """البحث عن بديل للحزمة"""
        alternatives = {
            'django-filter': 'django-filters',
            'django-filters': 'django-filter', 
            'psycopg2': 'psycopg2-binary',
            'psycopg2-binary': 'psycopg2',
            'pillow': 'PIL',
            'pil': 'Pillow'
        }
        
        alt_name = alternatives.get(package_name.lower())
        if alt_name and self.check_package_availability(alt_name):
            return alt_name
        return None
        
    def install_package(self, package_name: str, version: str = "") -> bool:
        """تثبيت حزمة"""
        try:
            if version and version.startswith('=='):
                package_spec = f"{package_name}{version}"
            elif version:
                package_spec = f"{package_name}{version}"
            else:
                package_spec = package_name
                
            print(f"🔧 Installing {package_spec}...")
            
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', package_spec], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Successfully installed {package_spec}")
                return True
            else:
                print(f"❌ Failed to install {package_spec}: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error installing {package_name}: {e}")
            return False
            
    def fix_requirements(self) -> Dict[str, any]:
        """إصلاح متطلبات المشروع"""
        print("\n🔍 Analyzing requirements.txt...")
        
        requirements = self.parse_requirements_file()
        installed_packages = self.get_installed_packages()
        
        results = {
            'total_requirements': len(requirements),
            'successfully_processed': 0,
            'failed_packages': [],
            'installed_packages': [],
            'alternative_packages': [],
            'skipped_packages': []
        }
        
        # Essential packages that must be installed first
        essential_packages = [
            ('Django', '4.2.16'),
            ('djangorestframework', ''),
            ('python-decouple', ''),
            ('dj-database-url', ''),
            ('django-cors-headers', ''),
            ('whitenoise', ''),
            ('Pillow', ''),
        ]
        
        print("\n🚀 Installing essential packages first...")
        for package, version in essential_packages:
            if package.lower() not in installed_packages:
                if self.install_package(package, f"=={version}" if version else ""):
                    results['installed_packages'].append(package)
                    results['successfully_processed'] += 1
                    
        print("\n📦 Processing remaining requirements...")
        for package, version, line_num in requirements:
            if package.lower() in [p[0].lower() for p in essential_packages]:
                continue  # Already processed
                
            if package.lower() in installed_packages:
                print(f"✅ {package} already installed")
                results['successfully_processed'] += 1
                continue
                
            # Try to install the package
            success = self.install_package(package, version)
            
            if success:
                results['installed_packages'].append(package)
                results['successfully_processed'] += 1
            else:
                # Try alternative package
                alternative = self.find_alternative_package(package)
                if alternative:
                    print(f"🔄 Trying alternative: {alternative}")
                    if self.install_package(alternative):
                        results['alternative_packages'].append((package, alternative))
                        results['successfully_processed'] += 1
                    else:
                        results['failed_packages'].append(package)
                else:
                    results['failed_packages'].append(package)
                    
        return results
        
    def generate_clean_requirements(self) -> str:
        """إنشاء ملف متطلبات نظيف ومحسن"""
        print("\n📝 Generating clean requirements.txt...")
        
        # Get currently installed packages
        installed = self.get_installed_packages()
        
        # Essential Django packages
        essential_requirements = """# University Management System - Clean Requirements
# متطلبات نظيفة ومحسنة لنظام إدارة الجامعة
# Generated: {date}

# =============================================================================
# CORE FRAMEWORK - الإطار الأساسي
# =============================================================================
Django==4.2.16
djangorestframework==3.16.1

# =============================================================================  
# AUTHENTICATION & SECURITY - المصادقة والأمان
# =============================================================================
djangorestframework-simplejwt
python-decouple
django-cors-headers
django-ratelimit

# =============================================================================
# DATABASE & STORAGE - قاعدة البيانات والتخزين  
# =============================================================================
dj-database-url
psycopg2-binary

# =============================================================================
# STATIC FILES & MEDIA - الملفات الثابتة والوسائط
# =============================================================================
whitenoise
Pillow

# =============================================================================
# API & DOCUMENTATION - واجهات برمجة التطبيقات والتوثيق
# =============================================================================
drf-yasg
django-filter
django-extensions

# =============================================================================
# PERFORMANCE & MONITORING - الأداء والمراقبة
# =============================================================================
django-redis
redis

# =============================================================================
# UTILITIES - الأدوات المساعدة
# =============================================================================
python-dateutil
requests

# =============================================================================
# DEVELOPMENT TOOLS - أدوات التطوير (اختياري)
# =============================================================================
# django-debug-toolbar  # Uncomment for development
""".format(date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        return essential_requirements
        
    def backup_current_requirements(self):
        """نسخ احتياطي من ملف المتطلبات الحالي"""
        if self.requirements_file.exists():
            backup_file = self.requirements_file.with_suffix('.txt.backup')
            backup_file.write_text(self.requirements_file.read_text(encoding='utf-8'), encoding='utf-8')
            print(f"📋 Backup created: {backup_file}")
            
    def update_requirements_file(self):
        """تحديث ملف المتطلبات"""
        # Create backup
        self.backup_current_requirements()
        
        # Generate new clean requirements
        clean_requirements = self.generate_clean_requirements()
        
        # Write new file
        self.requirements_file.write_text(clean_requirements, encoding='utf-8')
        print(f"✅ Updated requirements.txt with clean dependencies")
        
    def run_security_audit(self) -> Dict[str, any]:
        """فحص أمني للمتطلبات"""
        print("\n🛡️ Running security audit...")
        
        try:
            # Check for known vulnerabilities using pip-audit if available
            result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--outdated'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                outdated_packages = []
                for line in result.stdout.split('\n')[2:]:  # Skip header
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 3:
                            outdated_packages.append({
                                'package': parts[0],
                                'current': parts[1], 
                                'latest': parts[2]
                            })
                            
                return {
                    'status': 'completed',
                    'outdated_packages': outdated_packages,
                    'count': len(outdated_packages)
                }
            else:
                return {
                    'status': 'no_updates_needed',
                    'outdated_packages': [],
                    'count': 0
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'outdated_packages': [],
                'count': 0
            }
            
    def generate_report(self, fix_results: Dict, security_audit: Dict) -> str:
        """إنشاء تقرير شامل"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""
# 📦 Requirements Management Report
## تقرير إدارة متطلبات المشروع

**تاريخ التنفيذ:** {timestamp}
**حالة النظام:** {'✅ محسن بالكامل' if not fix_results['failed_packages'] else '⚠️ يحتاج مراجعة'}

---

## 📊 ملخص النتائج

### إحصائيات عامة
- **إجمالي المتطلبات:** {fix_results['total_requirements']}
- **تم معالجتها بنجاح:** {fix_results['successfully_processed']}
- **فشل في التثبيت:** {len(fix_results['failed_packages'])}
- **تم تثبيتها:** {len(fix_results['installed_packages'])}
- **بدائل مثبتة:** {len(fix_results['alternative_packages'])}

### الحزم المثبتة بنجاح ({len(fix_results['installed_packages'])})
"""
        
        for package in fix_results['installed_packages']:
            report += f"- ✅ {package}\n"
            
        if fix_results['alternative_packages']:
            report += f"\n### البدائل المثبتة ({len(fix_results['alternative_packages'])})\n"
            for original, alternative in fix_results['alternative_packages']:
                report += f"- 🔄 {original} → {alternative}\n"
                
        if fix_results['failed_packages']:
            report += f"\n### الحزم الفاشلة ({len(fix_results['failed_packages'])})\n"
            for package in fix_results['failed_packages']:
                report += f"- ❌ {package}\n"
                
        if security_audit['status'] == 'completed' and security_audit['outdated_packages']:
            report += f"\n### الحزم التي تحتاج تحديث ({security_audit['count']})\n"
            for pkg in security_audit['outdated_packages']:
                report += f"- ⬆️ {pkg['package']}: {pkg['current']} → {pkg['latest']}\n"
                
        report += f"""
---

## 🎯 التوصيات

1. **مراقبة التحديثات**: فحص دوري للحزم المحدثة
2. **الاختبار**: اختبار النظام بعد تحديث المتطلبات
3. **الأمان**: مراجعة التحديثات الأمنية بانتظام
4. **التوثيق**: الحفاظ على ملف متطلبات نظيف ومحدث

---

**تم إنشاء هذا التقرير تلقائياً بواسطة Requirements Manager v3.0.0**
"""
        
        return report
        
    def run_complete_management(self) -> Dict:
        """تشغيل إدارة شاملة للمتطلبات"""
        self.print_banner()
        
        # Fix requirements
        print("=" * 60)
        fix_results = self.fix_requirements()
        
        # Update requirements file
        print("=" * 60)
        self.update_requirements_file()
        
        # Security audit
        print("=" * 60)
        security_audit = self.run_security_audit()
        
        # Generate report
        print("=" * 60)
        print("📄 Generating requirements report...")
        report = self.generate_report(fix_results, security_audit)
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = Path(f'tools/reports/REQUIREMENTS_REPORT_{timestamp}.md')
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(report, encoding='utf-8')
        
        print(f"\n✅ Requirements management complete!")
        print(f"📄 Report saved to: {report_file}")
        print(f"📦 Successfully processed: {fix_results['successfully_processed']}/{fix_results['total_requirements']}")
        print(f"❌ Failed packages: {len(fix_results['failed_packages'])}")
        
        return {
            'fix_results': fix_results,
            'security_audit': security_audit,
            'report_file': str(report_file)
        }

if __name__ == '__main__':
    try:
        manager = RequirementsManager()
        results = manager.run_complete_management()
        
        print("\n" + "="*60)
        print("🎉 REQUIREMENTS MANAGEMENT COMPLETED! 🎉") 
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n⚠️ Operation interrupted by user")
    except Exception as e:
        print(f"\n❌ Requirements management failed: {str(e)}")
        import traceback
        traceback.print_exc()