import { Module } from '@nestjs/common';

import { AuthModule } from '../auth/auth.module';
import { PrismaService } from '../prisma.service';
import { TripsController } from './trips.controller';
import { TripsService } from './trips.service';

@Module({
    imports: [AuthModule],
    controllers: [TripsController],
    providers: [
        TripsService,
        PrismaService,
    ],
    exports: [TripsService],
})
export class TripsModule {}
