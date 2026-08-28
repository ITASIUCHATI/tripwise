import { Module } from '@nestjs/common';
import { JwtModule } from '@nestjs/jwt';

import { AuthController } from './auth.controller';
import { AuthService } from './auth.service';
import { JwtAuthGuard } from './jwt-auth.guard';
import { PrismaService } from '../prisma.service';

@Module({
    imports: [
        JwtModule.register({
            secret:
                process.env.JWT_SECRET ||
                'development-secret',
            signOptions: {
                expiresIn: '7d',
            },
        }),
    ],
    controllers: [AuthController],
    providers: [
        AuthService,
        JwtAuthGuard,
        PrismaService,
    ],
    exports: [
        AuthService,
        JwtAuthGuard,
        JwtModule,
    ],
})
export class AuthModule {}
