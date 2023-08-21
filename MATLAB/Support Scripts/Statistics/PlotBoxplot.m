
%% Clear workspace
clear
%close all

Error_type = "/ErrorTesting.csv";

%% Select set of results
ResultSet1 = "./Multiple/NARMA/20/10";
ResultSet2 = "./Multiple/NARMA/20/100";
ResultSet3 = "./Multiple/NARMA/20/200";
ResultSet4 = "./Multiple/NARMA/20/400";

ResultSet5 = "./Multiple/NARMA/200/10";
ResultSet6 = "./Multiple/NARMA/200/100";
ResultSet7 = "./Multiple/NARMA/200/200";
ResultSet8 = "./Multiple/NARMA/200/400";

%% Import CVS

ErrorSet1 = readmatrix([fullfile(ResultSet1,Error_type)]); % 0.0025 -



ErrorSet2 = readmatrix([fullfile(ResultSet2,Error_type)]); % 0.025 - 
ErrorSet3 = readmatrix([fullfile(ResultSet3,Error_type)]); % 0.05 -
ErrorSet4 = readmatrix([fullfile(ResultSet4,Error_type)]); % 0.1 -

ErrorSet5 = readmatrix([fullfile(ResultSet5,Error_type)]); % 0.025 -

ErrorSet6 = readmatrix([fullfile(ResultSet6,Error_type)]); % 0.25
ErrorSet7 = readmatrix([fullfile(ResultSet7,Error_type)]); % 0.5
ErrorSet8 = readmatrix([fullfile(ResultSet8,Error_type)]); % 1

%% Rescale

indicesErrorSet1 = find(abs(ErrorSet1)>1);
ErrorSet1(indicesErrorSet1) = [1];

indicesErrorSet2 = find(abs(ErrorSet2)>1);
ErrorSet2(indicesErrorSet2) = [1];

indicesErrorSet3 = find(abs(ErrorSet3)>1);
ErrorSet3(indicesErrorSet3) = [1];

indicesErrorSet4 = find(abs(ErrorSet4)>1);
ErrorSet4(indicesErrorSet4) = [1];

indicesErrorSet5 = find(abs(ErrorSet5)>1);
ErrorSet5(indicesErrorSet5) = [1];

indicesErrorSet6 = find(abs(ErrorSet6)>1);
ErrorSet6(indicesErrorSet6) = [1];

indicesErrorSet7 = find(abs(ErrorSet7)>1);
ErrorSet7(indicesErrorSet7) = [1];

indicesErrorSet8 = find(abs(ErrorSet8)>1);
ErrorSet8(indicesErrorSet8) = [1];

%% Order
% 1 2-5 3 4 7 8


%% Plot

Red = [1 0 0]';
Blue = [0 0 1]';
colors = [Red,Red,Red,Blue,Blue,Red,Blue,Blue]';

subplot(1,2,1);
Data = [ErrorSet1',ErrorSet2',ErrorSet5',ErrorSet3',ErrorSet4',ErrorSet6',ErrorSet7',ErrorSet8'];

boxplot(Data,'Labels',{'0.0025','0.025','0.025','0.05','0.1','0.25','0.5','1'})

xlabel('ρ');
ylabel('NRMSE');
title('NARMA-10');

h = findobj(gca,'Tag','Box');

for j=1:length(h)
    patch(get(h(j),'XData'),get(h(j),'YData'),colors(j,:),'FaceAlpha',.5);
end

legend({'20-Node System','200-Node System'})
grid on;

%% Select set of results
ResultSet1 = "./Multiple/santafe/20/10";
ResultSet2 = "./Multiple/santafe/20/100";
ResultSet3 = "./Multiple/santafe/20/200";
ResultSet4 = "./Multiple/santafe/20/400";

ResultSet5 = "./Multiple/santafe/200/10";
ResultSet6 = "./Multiple/santafe/200/100";
ResultSet7 = "./Multiple/santafe/200/200";
ResultSet8 = "./Multiple/santafe/200/400";

%% Import CVS

ErrorSet1 = readmatrix([fullfile(ResultSet1,Error_type)]); % 0.0025 -



ErrorSet2 = readmatrix([fullfile(ResultSet2,Error_type)]); % 0.025 - 
ErrorSet3 = readmatrix([fullfile(ResultSet3,Error_type)]); % 0.05 -
ErrorSet4 = readmatrix([fullfile(ResultSet4,Error_type)]); % 0.1 -

ErrorSet5 = readmatrix([fullfile(ResultSet5,Error_type)]); % 0.025 -

ErrorSet6 = readmatrix([fullfile(ResultSet6,Error_type)]); % 0.25
ErrorSet7 = readmatrix([fullfile(ResultSet7,Error_type)]); % 0.5
ErrorSet8 = readmatrix([fullfile(ResultSet8,Error_type)]); % 1

%% Rescale

indicesErrorSet1 = find(abs(ErrorSet1)>1);
ErrorSet1(indicesErrorSet1) = [1];

indicesErrorSet2 = find(abs(ErrorSet2)>1);
ErrorSet2(indicesErrorSet2) = [1];

indicesErrorSet3 = find(abs(ErrorSet3)>1);
ErrorSet3(indicesErrorSet3) = [1];

indicesErrorSet4 = find(abs(ErrorSet4)>1);
ErrorSet4(indicesErrorSet4) = [1];

indicesErrorSet5 = find(abs(ErrorSet5)>1);
ErrorSet5(indicesErrorSet5) = [1];

indicesErrorSet6 = find(abs(ErrorSet6)>1);
ErrorSet6(indicesErrorSet6) = [1];

indicesErrorSet7 = find(abs(ErrorSet7)>1);
ErrorSet7(indicesErrorSet7) = [1];

indicesErrorSet8 = find(abs(ErrorSet8)>1);
ErrorSet8(indicesErrorSet8) = [1];

%% Order
% 1 2-5 3 4 7 8


%% Plot

subplot(1,2,2);
Data = [ErrorSet1',ErrorSet2',ErrorSet5',ErrorSet3',ErrorSet4',ErrorSet6',ErrorSet7',ErrorSet8'];
boxplot(Data,'Labels',{'0.0025','0.025','0.025','0.05','0.1','0.25','0.5','1'})
xlabel('ρ');
ylabel('NRMSE');
title('Santa Fe');

h = findobj(gca,'Tag','Box');

for j=1:length(h)
    patch(get(h(j),'XData'),get(h(j),'YData'),colors(j,:),'FaceAlpha',.5);
end
grid on;
legend({'20-Node System','200-Node System'})