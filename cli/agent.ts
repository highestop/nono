#!/usr/bin/env node

import { AnthropicBedrock } from '@anthropic-ai/bedrock-sdk';
import * as readline from 'readline';

// Check required environment variables
const tryGetRequiredEnvVars = () => {
  const requiredVars = [
    { name: 'AWS_REGION', value: process.env.AWS_REGION },
    { name: 'AWS_PROFILE | CLAUDE_CODE_AWS_PROFILE', value: process.env.AWS_PROFILE || process.env.CLAUDE_CODE_AWS_PROFILE },
    { name: 'ANTHROPIC_MODEL', value: process.env.ANTHROPIC_MODEL }
  ];

  const missingVars = requiredVars.filter(envVar => !envVar.value);

  if (missingVars.length > 0) {
    console.error('❌ Missing required environment variables:');
    missingVars.forEach(envVar => {
      console.error(`   - ${envVar.name}`);
    });
    console.error('\nPlease set all required environment variables before running the agent.');
    process.exit(1);
  }

  return { region: requiredVars[0].value!, profile: requiredVars[1].value!, model: requiredVars[2].value! };
};

// Validate and get environment variables
const { region, profile, model } = tryGetRequiredEnvVars();

// Parse command line arguments
const parseArgs = () => {
  const args = process.argv.slice(2);
  const inputIndex = args.indexOf('--input');

  if (inputIndex !== -1 && inputIndex + 1 < args.length) {
    return args[inputIndex + 1];
  }

  return 'Hello Claude! Please introduce yourself.';
};

const userInput = parseArgs();

// Create Bedrock client with AWS configuration
const anthropic = new AnthropicBedrock({
  awsRegion: region,
});

async function main() {
  try {
    console.log('🤖 Starting Anthropic Agent...');

    // Check AWS configuration
    console.log(`🔧 Using AWS Region: ${region}`);
    console.log(`🔧 Using AWS Profile: ${profile}`);
    console.log(`🔧 Using Model: ${model}`);
    console.log(`📝 User Input: ${userInput}`);

    console.log('📡 Creating streaming message...');

    // Create a streaming message
    const stream = await anthropic.messages.create({
      model,
      max_tokens: 1000,
      messages: [
        {
          role: 'user',
          content: userInput
        }
      ],
      stream: true,
    });

    console.log('💬 Agent Messages (streaming):');
    console.log('='.repeat(50));
    console.log('💡 Press ESC to abort the stream...\n');

    const streamState = {
      fullResponse: '',
      inputTokens: 0,
      outputTokens: 0,
      messageModel: '',
      isAborted: false
    };

    // Setup keyboard input monitoring
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    // Set raw mode to capture individual key presses
    if (process.stdin.isTTY) {
      process.stdin.setRawMode(true);
    }

    // Listen for ESC key (ASCII 27)
    const keyHandler = (data: Buffer) => {
      const key = data[0];
      if (key === 27) { // ESC key
        streamState.isAborted = true;
        console.log('\n🛑 Stream aborted by user (ESC pressed)');
        stream.controller?.abort();
      }
    };

    process.stdin.on('data', keyHandler);

    try {
      // Process streaming response
      for await (const event of stream) {
        if (streamState.isAborted) break;

        if (event.type === 'message_start') {
          streamState.messageModel = event.message.model;
          streamState.inputTokens = event.message.usage.input_tokens;
          console.log('📝 Starting message stream...');
        } else if (event.type === 'content_block_delta') {
          if (event.delta.type === 'text_delta') {
            process.stdout.write(event.delta.text);
            streamState.fullResponse += event.delta.text;
          }
        } else if (event.type === 'message_delta') {
          if (event.usage) {
            streamState.outputTokens = event.usage.output_tokens;
          }
        } else if (event.type === 'message_stop') {
          console.log('\n' + '-'.repeat(30));
          console.log('✅ Stream completed');
        }
      }
    } finally {
      // Cleanup
      process.stdin.off('data', keyHandler);
      if (process.stdin.isTTY) {
        process.stdin.setRawMode(false);
      }
      rl.close();
    }

    console.log('✅ Agent execution completed');
    console.log(`📊 Usage statistics:`);
    console.log(`  - Input tokens: ${streamState.inputTokens}`);
    console.log(`  - Output tokens: ${streamState.outputTokens}`);
    console.log(`  - Model: ${streamState.messageModel}`);
    console.log(`  - Response length: ${streamState.fullResponse.length} characters`);

  } catch (error) {
    console.error('❌ Agent execution failed:', error);

    if (error instanceof Error) {
      console.error(`Error: ${error.message}`);
      console.error('Stack:', error.stack);
    } else {
      console.error('Unknown error:', error);
    }

    process.exit(1);
  }
}

// Run main function
main().catch(console.error);