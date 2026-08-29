import { Body, Controller, Post, Req, UseGuards } from '@nestjs/common';

import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { RecommendationsService } from './recommendations.service';

@Controller('recommendations')
@UseGuards(JwtAuthGuard)
export class RecommendationsController {
    constructor(
        private readonly recommendationsService: RecommendationsService,
    ) {}

    @Post('suggest-destination')
    suggestDestination(@Body() body: { destination: string }) {
        return this.recommendationsService.suggestDestination(body.destination);
    }

    @Post('destination-options')
    destinationOptions(@Body() body: { destination: string }) {
        return this.recommendationsService.destinationOptions(body.destination);
    }

    @Post('plan')
    plan(@Req() request: any, @Body() body: any) {
        return this.recommendationsService.plan(body, Number(request.user.sub));
    }
}
