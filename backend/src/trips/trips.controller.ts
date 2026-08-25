import {
    Body,
    Controller,
    Get,
    Post,
} from '@nestjs/common';

import { TripsService } from './trips.service';

@Controller('trips')
export class TripsController {
    constructor(
        private readonly tripsService: TripsService,
    ) {}

    @Get()
    list() {
        return this.tripsService.list();
    }

    @Get('stats')
    stats() {
        return this.tripsService.stats();
    }

    @Post()
    create(@Body() body: any) {
        return this.tripsService.create(body);
    }
}