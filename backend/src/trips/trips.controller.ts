import {
    Body,
    Controller,
    Get,
    Post,
    Req,
    UseGuards,
} from '@nestjs/common';

import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { TripsService } from './trips.service';

@Controller('trips')
@UseGuards(JwtAuthGuard)
export class TripsController {
    constructor(
        private readonly tripsService: TripsService,
    ) {}

    @Get()
    list(@Req() request: any) {
        return this.tripsService.list(
            Number(request.user.sub),
        );
    }

    @Get('stats')
    stats(@Req() request: any) {
        return this.tripsService.stats(
            Number(request.user.sub),
        );
    }

    @Post()
    create(
        @Req() request: any,
        @Body() body: any,
    ) {
        return this.tripsService.create({
            ...body,
            userId: Number(request.user.sub),
        });
    }
}
