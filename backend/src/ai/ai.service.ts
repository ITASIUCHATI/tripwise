import { Injectable } from '@nestjs/common';
import OpenAI from 'openai';

@Injectable()
export class AiService {
    async chat(
        message: string,
        context: any,
    ) {
        if (!process.env.OPENAI_API_KEY) {
            return {
                answer:
                    'AI assistant is not configured yet. Add OPENAI_API_KEY to enable natural-language travel advice.',
            };
        }

        const client = new OpenAI({
            apiKey: process.env.OPENAI_API_KEY,
        });

        const completion =
            await client.chat.completions.create({
                model: 'gpt-4o-mini',
                messages: [
                    {
                        role: 'system',
                        content:
                            'You are TripWise, a concise travel planning assistant. Use the supplied ML results as facts and do not invent numerical predictions.',
                    },
                    {
                        role: 'user',
                        content: `User request: ${message}\nML results: ${JSON.stringify(context)}`,
                    },
                ],
                temperature: 0.3,
            });

        return {
            answer:
                completion.choices[0]?.message?.content ||
                'No answer generated.',
        };
    }
}