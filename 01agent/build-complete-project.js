const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

console.log('🚀 Building Complete 01Agent Project...');
console.log('=====================================');

const platform = os.platform();
const arch = os.arch();
const startTime = Date.now();

// Project structure
const components = {
    backend: {
        name: 'Backend API',
        path: 'backend',
        buildCommand: 'pip install -r requirements.txt',
        testCommand: 'python -m pytest tests/',
        icon: '🔧'
    },
    desktop: {
        name: 'Desktop Application',
        path: 'desktop',
        buildCommand: 'npm run clean-build',
        testCommand: 'npm test',
        icon: '🖥️'
    },
    aiagent: {
        name: 'AI Agent Core',
        path: 'desktop/aiagent',
        buildCommand: 'pip install -r requirements.txt',
        testCommand: 'python -m pytest',
        icon: '🤖'
    },
    landingPage: {
        name: 'Landing Page',
        path: 'landing-page',
        buildCommand: 'echo "Static files ready"',
        testCommand: 'echo "No tests for static site"',
        icon: '🌐'
    }
};

// Step 1: Environment Check
console.log('\n🔍 Checking Environment...');
try {
    // Check Node.js
    const nodeVersion = execSync('node --version', { encoding: 'utf8' }).trim();
    console.log(`✅ Node.js: ${nodeVersion}`);

    // Check Python
    const pythonVersion = execSync('python --version', { encoding: 'utf8' }).trim();
    console.log(`✅ Python: ${pythonVersion}`);

    // Check npm
    const npmVersion = execSync('npm --version', { encoding: 'utf8' }).trim();
    console.log(`✅ npm: ${npmVersion}`);

    console.log(`✅ Platform: ${platform} (${arch})`);
} catch (error) {
    console.error('❌ Environment check failed:', error.message);
    process.exit(1);
}

// Step 2: Clean Previous Builds
console.log('\n🧹 Cleaning Previous Builds...');
const cleanDirs = [
    'desktop/dist',
    'desktop/01agent-app/build',
    'desktop/packages',
    'backend/__pycache__',
    'desktop/aiagent/__pycache__',
    'build-output'
];

cleanDirs.forEach(dir => {
    try {
        if (fs.existsSync(dir)) {
            fs.rmSync(dir, { recursive: true, force: true });
            console.log(`✅ Cleaned ${dir}`);
        }
    } catch (error) {
        console.warn(`⚠️ Could not clean ${dir}: ${error.message}`);
    }
});

// Create build output directory
const buildOutputDir = 'build-output';
if (!fs.existsSync(buildOutputDir)) {
    fs.mkdirSync(buildOutputDir, { recursive: true });
}

// Step 3: Build Each Component
console.log('\n🔨 Building Components...');
const buildResults = {};

for (const [key, component] of Object.entries(components)) {
    console.log(`\n${component.icon} Building ${component.name}...`);

    try {
        const componentPath = path.resolve(component.path);

        if (!fs.existsSync(componentPath)) {
            console.log(`⚠️ Skipping ${component.name} - path not found: ${componentPath}`);
            buildResults[key] = { status: 'skipped', reason: 'Path not found' };
            continue;
        }

        const buildStart = Date.now();

        // Execute build command
        console.log(`   Running: ${component.buildCommand}`);
        execSync(component.buildCommand, {
            stdio: 'inherit',
            cwd: componentPath,
            timeout: 300000 // 5 minutes timeout
        });

        const buildTime = Date.now() - buildStart;
        console.log(`✅ ${component.name} built successfully (${buildTime}ms)`);

        buildResults[key] = {
            status: 'success',
            buildTime,
            path: componentPath
        };

    } catch (error) {
        console.error(`❌ Failed to build ${component.name}:`, error.message);
        buildResults[key] = {
            status: 'failed',
            error: error.message
        };
    }
}

// Step 4: Run Tests
console.log('\n🧪 Running Tests...');
const testResults = {};

for (const [key, component] of Object.entries(components)) {
    if (buildResults[key]?.status !== 'success') {
        console.log(`⏭️ Skipping tests for ${component.name} (build failed)`);
        continue;
    }

    console.log(`\n${component.icon} Testing ${component.name}...`);

    try {
        const testStart = Date.now();

        console.log(`   Running: ${component.testCommand}`);
        execSync(component.testCommand, {
            stdio: 'inherit',
            cwd: path.resolve(component.path),
            timeout: 180000 // 3 minutes timeout
        });

        const testTime = Date.now() - testStart;
        console.log(`✅ ${component.name} tests passed (${testTime}ms)`);

        testResults[key] = {
            status: 'passed',
            testTime
        };

    } catch (error) {
        console.warn(`⚠️ Tests failed for ${component.name}:`, error.message);
        testResults[key] = {
            status: 'failed',
            error: error.message
        };
    }
}

// Step 5: Package Distribution
console.log('\n📦 Creating Distribution Package...');
try {
    const distDir = path.join(buildOutputDir, '01agent-complete');

    if (fs.existsSync(distDir)) {
        fs.rmSync(distDir, { recursive: true, force: true });
    }
    fs.mkdirSync(distDir, { recursive: true });

    // Copy built components
    const copyTasks = [
        {
            from: 'desktop/01agent-app/build',
            to: path.join(distDir, 'frontend'),
            condition: () => fs.existsSync('desktop/01agent-app/build')
        },
        {
            from: 'backend',
            to: path.join(distDir, 'backend'),
            condition: () => fs.existsSync('backend')
        },
        {
            from: 'desktop/aiagent',
            to: path.join(distDir, 'aiagent'),
            condition: () => fs.existsSync('desktop/aiagent')
        },
        {
            from: 'landing-page',
            to: path.join(distDir, 'landing-page'),
            condition: () => fs.existsSync('landing-page')
        },
        {
            from: 'desktop/main.js',
            to: path.join(distDir, 'main.js'),
            condition: () => fs.existsSync('desktop/main.js')
        },
        {
            from: 'desktop/package.json',
            to: path.join(distDir, 'package.json'),
            condition: () => fs.existsSync('desktop/package.json')
        }
    ];

    copyTasks.forEach(task => {
        if (task.condition()) {
            try {
                fs.cpSync(task.from, task.to, { recursive: true });
                console.log(`✅ Copied ${task.from} → ${task.to}`);
            } catch (error) {
                console.warn(`⚠️ Failed to copy ${task.from}:`, error.message);
            }
        } else {
            console.log(`⏭️ Skipped ${task.from} (not found)`);
        }
    });

    // Create deployment README
    const deploymentReadme = `# 01Agent Complete Distribution

## 🚀 Quick Start

### Prerequisites
- Node.js 16+
- Python 3.8+
- npm or yarn

### Installation

1. **Install Dependencies**
   \`\`\`bash
   npm install
   pip install -r backend/requirements.txt
   pip install -r aiagent/requirements.txt
   \`\`\`

2. **Start Backend**
   \`\`\`bash
   cd backend
   python main.py
   \`\`\`

3. **Start Desktop App**
   \`\`\`bash
   npm start
   \`\`\`

4. **Deploy Landing Page**
   \`\`\`bash
   # Serve landing-page directory with any web server
   npx serve landing-page
   \`\`\`

## 📁 Structure

- \`frontend/\` - React frontend build
- \`backend/\` - FastAPI backend
- \`aiagent/\` - AI agent core
- \`landing-page/\` - Marketing website
- \`main.js\` - Electron main process
- \`package.json\` - Desktop app configuration

## 🔧 Configuration

### Environment Variables
Create \`.env\` files in:
- \`backend/.env\` - Backend configuration
- \`aiagent/.env\` - AI agent settings

### Build Information
- Built on: ${new Date().toISOString()}
- Platform: ${platform} (${arch})
- Node.js: ${execSync('node --version', { encoding: 'utf8' }).trim()}
- Python: ${execSync('python --version', { encoding: 'utf8' }).trim()}

## 📊 Build Results

${Object.entries(buildResults).map(([key, result]) =>
    `- ${components[key].name}: ${result.status} ${result.buildTime ? `(${result.buildTime}ms)` : ''}`
).join('\n')}

## 🧪 Test Results

${Object.entries(testResults).map(([key, result]) =>
    `- ${components[key].name}: ${result.status} ${result.testTime ? `(${result.testTime}ms)` : ''}`
).join('\n')}

## 🆘 Support

For support and documentation:
- Website: https://01agent.ai
- Documentation: https://docs.01agent.ai
- GitHub: https://github.com/01agent/01agent

---
Built with ❤️ by the 01Agent team
`;

    fs.writeFileSync(path.join(distDir, 'README.md'), deploymentReadme);

    // Create package info
    const packageInfo = {
        name: '01agent-complete',
        version: '2.0.0',
        description: '01Agent - Lightning-Fast AI Desktop Assistant - Complete Distribution',
        buildDate: new Date().toISOString(),
        platform: `${platform}-${arch}`,
        components: Object.keys(components),
        buildResults,
        testResults
    };

    fs.writeFileSync(
        path.join(distDir, 'build-info.json'),
        JSON.stringify(packageInfo, null, 2)
    );

    console.log(`✅ Distribution package created: ${distDir}`);

} catch (error) {
    console.error('❌ Failed to create distribution package:', error.message);
}

// Step 6: Generate Build Report
console.log('\n📋 Generating Build Report...');
const totalTime = Date.now() - startTime;
const successfulBuilds = Object.values(buildResults).filter(r => r.status === 'success').length;
const totalBuilds = Object.keys(buildResults).length;
const passedTests = Object.values(testResults).filter(r => r.status === 'passed').length;
const totalTests = Object.keys(testResults).length;

const buildReport = `# 01Agent Build Report

## 📊 Summary
- **Total Build Time**: ${totalTime}ms (${(totalTime / 1000).toFixed(2)}s)
- **Successful Builds**: ${successfulBuilds}/${totalBuilds}
- **Passed Tests**: ${passedTests}/${totalTests}
- **Platform**: ${platform} (${arch})
- **Date**: ${new Date().toISOString()}

## 🔨 Build Results

${Object.entries(buildResults).map(([key, result]) => `
### ${components[key].icon} ${components[key].name}
- **Status**: ${result.status}
- **Build Time**: ${result.buildTime || 'N/A'}ms
- **Path**: ${result.path || 'N/A'}
${result.error ? `- **Error**: ${result.error}` : ''}
`).join('\n')}

## 🧪 Test Results

${Object.entries(testResults).map(([key, result]) => `
### ${components[key].icon} ${components[key].name}
- **Status**: ${result.status}
- **Test Time**: ${result.testTime || 'N/A'}ms
${result.error ? `- **Error**: ${result.error}` : ''}
`).join('\n')}

## 🎯 Next Steps

${successfulBuilds === totalBuilds ?
    '✅ All components built successfully! Ready for deployment.' :
    '⚠️ Some components failed to build. Check the errors above and retry.'
}

### Deployment Checklist
- [ ] Backend API deployed and running
- [ ] Desktop app packaged for distribution
- [ ] Landing page deployed to web server
- [ ] AI agent dependencies installed
- [ ] Environment variables configured
- [ ] SSL certificates configured (production)
- [ ] Monitoring and logging set up

## 📁 Output Files
- Distribution package: \`build-output/01agent-complete/\`
- Build report: \`build-output/build-report.md\`
- Build info: \`build-output/01agent-complete/build-info.json\`

---
Generated by 01Agent Build System v2.0.0
`;

fs.writeFileSync(path.join(buildOutputDir, 'build-report.md'), buildReport);

// Step 7: Final Summary
console.log('\n🎉 Build Complete!');
console.log('==================');
console.log(`⏱️  Total Time: ${(totalTime / 1000).toFixed(2)}s`);
console.log(`✅ Successful Builds: ${successfulBuilds}/${totalBuilds}`);
console.log(`🧪 Passed Tests: ${passedTests}/${totalTests}`);
console.log(`📦 Distribution: build-output/01agent-complete/`);
console.log(`📋 Report: build-output/build-report.md`);

if (successfulBuilds === totalBuilds) {
    console.log('\n🚀 All components built successfully!');
    console.log('Ready for deployment and distribution.');

    // Success exit code
    process.exit(0);
} else {
    console.log('\n⚠️  Some components failed to build.');
    console.log('Check the build report for details.');

    // Warning exit code
    process.exit(1);
}