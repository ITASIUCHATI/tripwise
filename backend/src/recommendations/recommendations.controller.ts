import {
    Body,
    Controller,
    Post,
} from '@nestjs/common';

import { RecommendationsService } from './recommendations.service';

@Controller('recommendations')
export class RecommendationsController {
    constructor(
        private readonly recommendationsService: RecommendationsService,
    ) {}

    @Post('plan')
    plan(@Body() body: any) {
        return this.recommendationsService.plan(body);
    }
}