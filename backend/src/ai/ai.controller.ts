import {
    Body,
    Controller,
    Post,
} from '@nestjs/common';

import { AiService } from './ai.service';

class ChatDto {
    message!: string;
    context: any;
}

@Controller('ai')
export class AiController {
    constructor(
        private readonly aiService: AiService,
    ) {}

    @Post('chat')
    chat(@Body() body: ChatDto) {
        return this.aiService.chat(
            body.message,
            body.context,
        );
    }
}